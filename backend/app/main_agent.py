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
from app.state import AgentState

# ── State ─────────────────────────────────────────────────────────────────────
# class AgentState(MessagesState):
#     summary: str = ""

# Turn window: summarize every N completed turns
TURNS_PER_WINDOW = 2

# ── Turn detection helpers ────────────────────────────────────────────────────
def get_completed_turns(messages: list[BaseMessage]) -> list[list[BaseMessage]]:
    """Groups messages into turns: user_query → ... → format_response/final_response."""
    turns = []
    current_turn: list[BaseMessage] = []

    for msg in messages:
        if isinstance(msg, HumanMessage) and getattr(msg, "name", None) == "user_query":
            if current_turn:
                turns.append(current_turn)
            current_turn = [msg]
        else:
            current_turn.append(msg)
            if isinstance(msg, AIMessage) and getattr(msg, "name", None) in ("format_response", "final_response"):
                turns.append(current_turn)
                current_turn = []

    if current_turn:
        turns.append(current_turn)

    logger.info(f"[turn_detection] total turns in state: {len(turns)}")
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

    if len(turns) < TURNS_PER_WINDOW:
        logger.info(f"[summarize] only {len(turns)} turns — skipping (need {TURNS_PER_WINDOW})")
        return {}

    # Take the oldest TURNS_PER_WINDOW completed turns
    summarizable_turns = turns[:TURNS_PER_WINDOW]
    messages_to_delete = [msg for turn in summarizable_turns for msg in turn]

    # Build rich context from ALL messages in the turns
    readable_context = []
    for i, turn in enumerate(summarizable_turns):
        lines = [f"--- Turn {i + 1} ---"]
        for msg in turn:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            node_name = getattr(msg, "name", "unknown")
            content = msg.content

            if node_name == "format_response":
                try:
                    content = f"Final Answer: {json.loads(content).get('answer', '')}"
                except Exception:
                    pass
            elif node_name == "write_sql_query":
                try:
                    content = f"Generated SQL: {json.loads(content).get('candidate_sql', '')}"
                except Exception:
                    pass
            elif node_name == "rewrite_user_query":
                try:
                    content = f"Normalized Query: {json.loads(content).get('normalized_query', '')}"
                except Exception:
                    pass

            lines.append(f"[{role} - {node_name}] {content}")
        readable_context.append("\n".join(lines))

    logger.info(f"[summarize] summarizing {len(summarizable_turns)} turns. existing_summary length={len(existing_summary)}")

    prompt = (
        f"You are a memory manager for a SQL database assistant. "
        f"Update the existing summary below by incorporating the new turns. "
        f"Keep it concise but capture tables, questions, and key results.\n\n"
        f"EXISTING SUMMARY:\n{existing_summary}\n\nNEW TURNS:\n"
        if existing_summary else
        "Summarize the following conversation turns between a user and a SQL database assistant. "
        "Capture tables queried, key questions, and answers.\n\n"
    ) + "\n\n".join(readable_context)

    # Plain LLM call — response.content is just a string (the summary text)
    llm = ChatGroq(model="openai/gpt-oss-120b", groq_api_key=os.getenv("GROQ_API_KEY"))
    response  = llm.invoke([
        SystemMessage(content="Create/update a concise technical summary of user-assistant SQL database interactions."),
        HumanMessage(content=prompt)
    ])

    new_summary = response.content
    
    
    logger.info(f"[summarize] new summary generated ({len(new_summary)} chars). pruning {len(messages_to_delete)} messages.")

    # Correct return: update summary field + delete the old messages
    delete_ops = [RemoveMessage(id=m.id) for m in messages_to_delete]
    # logger.info(f"[summarize] {state['summary'] or ''}  ")
    logger.info(f"[summarize] {state['messages'][-1]}  ")

    return {"summary": response.content, "messages": delete_ops}

# ── Routing functions ─────────────────────────────────────────────────────────
def route_after_decider(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if getattr(msg, "name", None) == "final_response":
            return "after_final"
        if getattr(msg, "name", None) == "decider_node":
            return "rewrite_user_query"
        break
    return "rewrite_user_query"


def route_after_final(state: AgentState) -> str:
    """After a non-DB response, check if we should summarize."""
    if count_completed_turns(state["messages"]) > TURNS_PER_WINDOW:
        return "summarize_conversation"
    return END


def route_validation(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if getattr(msg, "name", None) == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                return "execute_sql_query" if data.is_valid else "rewrite_user_query"
            except Exception:
                pass
            break
    return "rewrite_user_query"


def route_after_format(state: AgentState) -> str:
    """After a full DB pipeline response, check if we should summarize."""
    if count_completed_turns(state["messages"]) > TURNS_PER_WINDOW:
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

    workflow.add_edge(START, "decider_node")

    workflow.add_conditional_edges(
        "decider_node",
        route_after_decider,
        {
            "rewrite_user_query": "rewrite_user_query",
            "after_final": "summarize_conversation",
        }
    )

    workflow.add_edge("rewrite_user_query", "get_tables_schemas")
    workflow.add_edge("get_tables_schemas", "write_sql_query")
    workflow.add_edge("write_sql_query", "validate_query")
    workflow.add_conditional_edges(
        "validate_query",
        route_validation,
        {
            "execute_sql_query": "execute_sql_query",
            "rewrite_user_query": "rewrite_user_query",
        }
    )
    workflow.add_edge("execute_sql_query", "format_response")
    workflow.add_conditional_edges(
        "format_response",
        route_after_format,
        {
            "summarize_conversation": "summarize_conversation",
            END: END,
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