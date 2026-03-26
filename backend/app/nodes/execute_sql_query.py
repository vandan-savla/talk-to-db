import json
import logging
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from app.pydantic_models.node_schemas import WriteSqlOutput, ExecuteSqlOutput
from app.tools.execute_sql_query_tool import execute_sql_query

logger = logging.getLogger(__name__)

def execute_sql_query_node(state: MessagesState) -> MessagesState:
    candidate_sql = ""
    for msg in reversed(state["messages"]):
        if msg.name == "write_sql_query":
            try:
                candidate_sql = WriteSqlOutput.model_validate_json(msg.content).candidate_sql
            except:
                pass
            break
    
    if candidate_sql:
        logger.info(f"Executing SQL query: {candidate_sql}...")
    else:
        logger.warning("No SQL query found in state to execute.")
    
    result = execute_sql_query(candidate_sql)

    # If error came back, short circuit
    if result and "error" in result[0]:
        logger.error(f"SQL execution error: {result[0]['error']}")
        return {
            "messages": [AIMessage(
                content=json.dumps({
                    "answer": "Sorry, I couldn't retrieve that data. Please rephrase your question.",
                    "sql_query": ""
                }),
                name="format_response"
            )]
        }

    logger.info(f"SQL execution successful. Retrieved {len(result)} rows.")
    output = ExecuteSqlOutput(sql_result=result)
    return {"messages": [AIMessage(content=output.model_dump_json(), name="execute_sql_query")]}