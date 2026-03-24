import logging
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import RemoveMessage, HumanMessage, SystemMessage, AIMessage, BaseMessage
from app.nodes.decider_node import decider_node
from app.nodes.rewrite_user_query import rewrite_user_query
from app.nodes.get_tables_schemas import get_tables_schemas
from app.nodes.write_sql_query import write_sql_query
from app.nodes.validate_query import validate_query
from app.nodes.execute_sql_query import execute_sql_query_node
from app.nodes.format_response import format_response
from app.pydantic_models.node_schemas import ValidateQueryOutput, DeciderOutput
from langchain_groq import ChatGroq
import sqlite3, os, json

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main_agent")

load_dotenv()

conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

class AgentState(MessagesState):
    summary: str

# ── Turn detection helper ─────────────────────────────────────────────────────
def get_completed_turns(messages: list[BaseMessage]) -> list[list[BaseMessage]]:
    """Groups messages into turns: (user_query -> ... -> final_response)."""
    turns = []
    current_turn = []
    
    for msg in messages:
        # A new turn starts with HumanMessage(name="user_query")
        if isinstance(msg, HumanMessage) and getattr(msg, 'name', None) == "user_query":
            if current_turn:
                turns.append(current_turn)
            current_turn = [msg]
        else:
            current_turn.append(msg)
            # A turn ends with a final AIMessage
            if isinstance(msg, AIMessage) and getattr(msg, 'name', None) in ["format_response", "final_response"]:
                turns.append(current_turn)
                current_turn = []
                
    if current_turn:
        turns.append(current_turn)
    logger.info(f"Turns: {turns}")
    return turns

def count_completed_turns(messages: list[BaseMessage]) -> int:
    """Counts only successfully completed User-Assistant exchanges."""
    count = 0
    for msg in messages:
        if isinstance(msg, AIMessage) and getattr(msg, 'name', None) in ["format_response", "final_response"]:
            count += 1
    logger.info(f"Count: {count}")
    return count

# ── Summarization node ────────────────────────────────────────────────────────
def summarize_conversation(state: AgentState):
    existing_summary = state.get("summary", "")
    all_messages = state["messages"]
    
    turns = get_completed_turns(all_messages)
    
    # We only summarize if we have 6 or more turns. 
    # Usually we summarize the first 6.
    if len(turns) < 6:
        return {}
    
    summarizable_turns = turns[:6]
    messages_to_delete = [msg for turn in summarizable_turns for msg in turn]
    
    # Build a rich readable context for the LLM from ALL messages in these turns
    readable_context = []
    for i, turn in enumerate(summarizable_turns):
        turn_text = [f"--- Turn {i+1} ---"]
        for msg in turn:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            node_name = getattr(msg, 'name', 'unknown')
            
            # Extract content based on node type for richer summary
            content = msg.content
            if node_name == "format_response":
                try:
                    data = json.loads(content)
                    content = f"Final Answer: {data.get('answer', '')}"
                except: pass
            elif node_name == "write_sql_query":
                try:
                    data = json.loads(content)
                    content = f"Generated SQL: {data.get('candidate_sql', '')}"
                except: pass
            elif node_name == "rewrite_user_query":
                try:
                    data = json.loads(content)
                    content = f"Normalized Query: {data.get('normalized_query', '')}"
                except: pass
            
            turn_text.append(f"[{role} - {node_name}] {content}")
        readable_context.append("\n".join(turn_text))

    logger.info(f"Summarizing the first 6 turns out of {len(turns)} available.")

    prompt = (
        f"You are a memory manager for a database assistant. Update the existing summary with these 6 new turns. "
        f"The existing summary is:\n{existing_summary}\n\n"
        f"NEW TURNS TO SUMMARIZE:\n"
        if existing_summary else
        "Summarize these first 6 conversation turns between a user and a database assistant. Capture key topics, tables queried, and answers.\n\n"
    ) + "\n\n".join(readable_context)

    llm = ChatGroq(model="openai/gpt-oss-120b", groq_api_key=os.getenv("GROQ_API_KEY"))
    response = llm.invoke([
        SystemMessage(content="Create/Update a concise but technically accurate summary of user-assistant interactions regarding a SQL database."),
        HumanMessage(content=prompt)
    ])

    delete = [RemoveMessage(id=m.id) for m in messages_to_delete]
    logger.info("Summarization complete. Pruning messages from the first 6 turns.")

    return {"summary": response.content, "messages": delete}

# ── Routing functions ─────────────────────────────────────────────────────────
def route_after_decider(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if msg.name == "final_response":
            return "after_final"
        if msg.name == "decider_node":
            return "rewrite_user_query"
        break
    return "rewrite_user_query"

def route_after_final(state: AgentState) -> str:
    """Check if we have at least 7 turns total; if so, summarize the first 6."""
    if count_completed_turns(state["messages"]) >= 7:
        return "summarize_conversation"
    return END

def route_validation(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                return "execute_sql_query" if data.is_valid else "rewrite_user_query"
            except:
                pass
            break
    return "rewrite_user_query"

def route_after_format(state: AgentState) -> str:
    """Check if we have at least 7 turns total; if so, summarize the first 6."""
    if count_completed_turns(state["messages"]) >= 7:
        return "summarize_conversation"
    return END

# ── Graph ─────────────────────────────────────────────────────────────────────
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("decider_node", decider_node)
    workflow.add_node("rewrite_user_query", rewrite_user_query)
    workflow.add_node("get_tables_schemas", get_tables_schemas)
    workflow.add_node("write_sql_query", write_sql_query)
    workflow.add_node("validate_query", validate_query)
    workflow.add_node("execute_sql_query", execute_sql_query_node)
    workflow.add_node("format_response", format_response)
    workflow.add_node("summarize_conversation", summarize_conversation)

    # Entry point
    workflow.add_edge(START, "decider_node")

    # After decider — branch to pipeline or skip
    workflow.add_conditional_edges(
        "decider_node",
        route_after_decider,
        {
            "rewrite_user_query": "rewrite_user_query",
            "after_final": "summarize_conversation",
        }
    )

    # Main pipeline
    workflow.add_edge("rewrite_user_query", "get_tables_schemas")
    workflow.add_edge("get_tables_schemas", "write_sql_query")
    workflow.add_edge("write_sql_query", "validate_query")
    workflow.add_conditional_edges(
        "validate_query",
        route_validation,
        {
            "execute_sql_query": "execute_sql_query",
            "rewrite_user_query": "rewrite_user_query"
        }
    )
    workflow.add_edge("execute_sql_query", "format_response")
    workflow.add_conditional_edges(
        "format_response",
        route_after_format,
        {
            "summarize_conversation": "summarize_conversation",
            END: END
        }
    )

    workflow.add_edge("summarize_conversation", END)

    return workflow.compile(checkpointer=checkpointer)

main_agent = build_graph()

# Generate graph visualization
try:
    graph_png = main_agent.get_graph().draw_mermaid_png()
    with open("graph_image.png", "wb") as f:
        f.write(graph_png)
    logger.info("Graph visualization updated.")
except Exception as e:
    logger.warning(f"Could not generate graph visualization: {e}")