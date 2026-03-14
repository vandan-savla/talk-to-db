from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from app.tools.execute_sql_query_tool import execute_sql_query as execute_sql_tool
from app.pydantic_models.node_schemas import WriteSqlOutput, ExecuteSqlOutput

def execute_sql_query(state: MessagesState) -> MessagesState:
    candidate_sql = ""
    for msg in reversed(state["messages"]):
        if msg.name == "write_sql_query":
            try:
                data = WriteSqlOutput.model_validate_json(msg.content)
                candidate_sql = data.candidate_sql
            except:
                pass
            break

    operation = "select" if candidate_sql.strip().lower().startswith("select") else "unknown"
    
    try:
        sql_result = execute_sql_tool.invoke({"sql_query": candidate_sql, "operation": operation})
    except Exception as e:
        sql_result = [{"error": str(e)}]
        
    final_output = ExecuteSqlOutput(
        sql_result=sql_result if isinstance(sql_result, list) else [sql_result]
    )
    
    return {"messages": [AIMessage(content=final_output.model_dump_json(), name="execute_sql_query")]}