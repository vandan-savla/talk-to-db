import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, List, Any, Dict
from langgraph.graph import END, START, StateGraph

from app.nodes.rewrite_user_query import rewrite_user_query
from app.nodes.get_tables_schemas import get_tables_schemas
from app.nodes.write_sql_query import write_sql_query
from app.nodes.validate_query import validate_query
from app.nodes.execute_sql_query import execute_sql_query

load_dotenv()


class AgentState(TypedDict, total=False):
    question: str
    normalized_question: str
    candidate_tables: List[Dict[str, Any]]
    schemas_text: str
    candidate_sql: str
    sql_result: List[Dict[str, Any]]
    answer: str

def route_validation(state):

    if state["is_valid"]:
        return "execute_sql_query"
    else:
        return "rewrite_user_query"

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("rewrite_user_query", rewrite_user_query)
    workflow.add_node("get_tables_schemas", get_tables_schemas)
    workflow.add_node("write_sql_query", write_sql_query)
    workflow.add_node("validate_query", validate_query)
    workflow.add_node("execute_sql_query", execute_sql_query)

    workflow.add_edge(START, "get_tables_schemas")
    workflow.add_edge("get_tables_schemas", "write_sql_query")
    workflow.add_edge("write_sql_query", "validate_query")

    workflow.add_conditional_edges(
        "validate_query",
        route_validation,
        {
            "execute_sql_query": "execute_sql_query",
            "rewrite_user_query": "rewrite_user_query",
        },
    )

    workflow.add_edge("execute_sql_query", END)
    app = workflow.compile()
    
    return app

main_agent = build_graph()