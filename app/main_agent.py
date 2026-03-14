from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph, MessagesState
from app.nodes.rewrite_user_query import rewrite_user_query
from app.nodes.get_tables_schemas import get_tables_schemas
from app.nodes.write_sql_query import write_sql_query
from app.nodes.validate_query import validate_query
from app.nodes.execute_sql_query import execute_sql_query
from app.nodes.format_response import format_response
from app.pydantic_models.node_schemas import ValidateQueryOutput

load_dotenv()

def route_validation(state: MessagesState):
    last_msg = state["messages"][-1]
    if last_msg.name == "validate_query":
        data = ValidateQueryOutput.model_validate_json(last_msg.content)
        if data.is_valid:
            return "execute_sql_query"
        else:
            return "rewrite_user_query"
    return "rewrite_user_query"

def build_graph():
    workflow = StateGraph(MessagesState)

    workflow.add_node("rewrite_user_query", rewrite_user_query)
    workflow.add_node("get_tables_schemas", get_tables_schemas)
    workflow.add_node("write_sql_query", write_sql_query)
    workflow.add_node("validate_query", validate_query)
    workflow.add_node("execute_sql_query", execute_sql_query)
    workflow.add_node("format_response", format_response)

    workflow.add_edge(START, "rewrite_user_query")
    workflow.add_edge("rewrite_user_query", "get_tables_schemas")
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

    workflow.add_edge("execute_sql_query", "format_response")
    workflow.add_edge("format_response", END)
    app = workflow.compile()
    
    return app

main_agent = build_graph()