import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, List, Any, Dict
from langgraph.graph import START, StateGraph

from app.nodes.rewrite_user_query  import rewrite_user_query 


load_dotenv()


class AgentState(TypedDict, total=False):
    question: str
    normalized_question: str
    candidate_tables: List[Dict[str, Any]]
    schemas_text: str
    candidate_sql: str
    sql_result: List[Dict[str, Any]]
    answer: str


def build_graph(query: str):
    workflow = StateGraph(AgentState)
    # Nodes
    workflow.add_node("query", query)
    workflow.add_node("rewrite_user_query", rewrite_user_query)
    workflow.add_node("get_schemas_text", get_schemas_text)
    workflow.add_node("write_sql_query", write_sql_query)
    workflow.add_node("execute_sql_query", execute_sql_query)
    workflow.add_node("answer", answer)

    # Edges 
    workflow.add_edge(START, "query")
    workflow.add_edge("query", "rewrite_query")
    workflow.add_edge("rewrite_query", "rewrite_user_query")
    workflow.add_edge("rewrite_user_query", "get_schemas_text")
    workflow.add_edge("get_schemas_text", "write_sql_query")
    workflow.add_edge("write_sql_query", "execute_sql_query")
    workflow.add_edge("execute_sql_query", "answer")

    app = workflow.compile()
    return app

main_agent = build_graph()