from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from app.pydantic_models.node_schemas import WriteSqlOutput, ExecuteSqlOutput
import json
from app.tools.execute_sql_query_tool import execute_sql_query

def execute_sql_query_node(state: MessagesState) -> MessagesState:
    candidate_sql = ""
    for msg in reversed(state["messages"]):
        if msg.name == "write_sql_query":
            try:
                candidate_sql = WriteSqlOutput.model_validate_json(msg.content).candidate_sql
            except:
                pass
            break

    result = execute_sql_query(candidate_sql)

    # If error came back, short circuit — don't send to format_response
    if result and "error" in result[0]:
        return {
            "messages": [AIMessage(
                content=json.dumps({
                    "answer": "Sorry, I couldn't retrieve that data. Please rephrase your question.",
                    "sql_query": ""
                }),
                name="format_response"  # name it format_response so API handler picks it up normally
            )]
        }

    output = ExecuteSqlOutput(sql_result=result)
    return {"messages": [AIMessage(content=output.model_dump_json(), name="execute_sql_query")]}