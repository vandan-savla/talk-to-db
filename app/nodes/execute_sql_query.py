from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import MessagesState
import os 
from app.tools.execute_sql_query_tool import execute_sql_query as execute_sql_tool
from app.pydantic_models.node_schemas import WriteSqlOutput, ExecuteSqlOutput, AnswerOutput

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
            
    query = state["messages"][0].content

    operation = "select" if candidate_sql.strip().lower().startswith("select") else "unknown"
    
    try:
        sql_result = execute_sql_tool.invoke({"sql_query": candidate_sql, "operation": operation})
    except Exception as e:
        sql_result = [{"error": str(e)}]
        
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant. Provide a natural language answer to the user's question based on the results of the SQL query. Keep the answer concise."),
        ("human", "User question: {query}\n\nSQL Query:\n{candidate_sql}\n\nSQL Result:\n{sql_result}")
    ])
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(AnswerOutput) 
    
    
    chain = prompt | model 
    
    response: AnswerOutput = chain.invoke({
        "query": query,
        "candidate_sql": candidate_sql,
        "sql_result": str(sql_result)
    })
    
    final_output = ExecuteSqlOutput(
        sql_result=sql_result if isinstance(sql_result, list) else [sql_result], 
        answer=response.answer
    )
    
    return {"messages": [AIMessage(content=final_output.model_dump_json(), name="execute_sql_query")]}