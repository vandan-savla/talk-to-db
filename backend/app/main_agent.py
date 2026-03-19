from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import RemoveMessage, HumanMessage, SystemMessage
from app.nodes.decider_node import decider_node
from app.nodes.rewrite_user_query import rewrite_user_query
from app.nodes.get_tables_schemas import get_tables_schemas
from app.nodes.write_sql_query import write_sql_query
from app.nodes.validate_query import validate_query
from app.nodes.execute_sql_query import execute_sql_query
from app.nodes.format_response import format_response
from app.pydantic_models.node_schemas import ValidateQueryOutput, DeciderOutput
from langchain_groq import ChatGroq
import sqlite3, os, json

load_dotenv()

conn = sqlite3.connect("agent_memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

class AgentState(MessagesState):
    summary: str

SUMMARIZE_AFTER = 12

# ── Summarization node ────────────────────────────────────────────────────────
def summarize_conversation(state: AgentState):
    existing_summary = state.get("summary", "")

    readable = []
    for msg in state["messages"]:
        if msg.name == "user_query":
            readable.append(f"User: {msg.content}")
        elif msg.name == "format_response":
            try:
                data = json.loads(msg.content)
                readable.append(f"Assistant: {data.get('answer', '')}")
            except:
                pass


    if not readable:
        return {}

    prompt = (
        f"Extend this existing summary:\n{existing_summary}\n\nNew messages:\n"
        if existing_summary else
        "Summarize this conversation between a user and a database assistant.\n\n"
    ) + "\n".join(readable)

    llm = ChatGroq(model="openai/gpt-oss-120b", groq_api_key=os.getenv("GROQ_API_KEY"))
    response = llm.invoke([
        SystemMessage(content="Summarize conversations between a user and a SQL database assistant. Capture tables queried, questions asked, and results."),
        HumanMessage(content=prompt)
    ])

    delete = [RemoveMessage(id=m.id) for m in state["messages"][:-6]]
    return {"summary": response.content, "messages": delete}

# ── Routing functions ─────────────────────────────────────────────────────────
def route_after_decider(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if msg.name == "final_response":
            # Decider said no → skip pipeline, go to summarize check
            return "after_final"
        if msg.name == "decider_node":
            # Decider said yes → run pipeline
            return "rewrite_user_query"
        break
    return "rewrite_user_query"

def route_after_final(state: AgentState) -> str:
    """After a final_response (decider said no), still check if summarization needed."""
    if len(state["messages"]) > SUMMARIZE_AFTER:
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
    if len(state["messages"]) > SUMMARIZE_AFTER:
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
    workflow.add_node("execute_sql_query", execute_sql_query)
    workflow.add_node("format_response", format_response)
    workflow.add_node("summarize_conversation", summarize_conversation)

    # Entry point
    workflow.add_edge(START, "decider_node")

    # After decider — branch to pipeline or skip
    workflow.add_conditional_edges(
        "decider_node",
        route_after_decider,
        {
            "rewrite_user_query": "rewrite_user_query",  # DB question → full pipeline
            "after_final": "summarize_conversation",      # small talk → just summarize if needed
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

graph_png = main_agent.get_graph().draw_mermaid_png()
with open("graph_image.png", "wb") as f:
    f.write(graph_png)