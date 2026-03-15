from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import MessagesState
import os 
from app.pydantic_models.node_schemas import FormatResponseOutput, ExecuteSqlOutput, WriteSqlOutput

def format_response(state: MessagesState) -> MessagesState:
    candidate_sql = ""
    sql_result = []
    
    for msg in reversed(state["messages"]):
        if msg.name == "write_sql_query" and not candidate_sql:
            try:
                data = WriteSqlOutput.model_validate_json(msg.content)
                candidate_sql = data.candidate_sql
            except:
                pass
        elif msg.name == "execute_sql_query" and not sql_result:
            try:
                data = ExecuteSqlOutput.model_validate_json(msg.content)
                sql_result = data.sql_result
            except:
                pass
        
        if candidate_sql and sql_result:
            break
            
    query = state["messages"][-1].content

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a helpful database assistant. Provide a natural language answer to the user's question based on the results of the SQL query. 
        If the SQL result contains multiple rows or columns, format the data as a clean Markdown table in your answer. 
        Also, return the exact SQL query that was executed in proper SQL format not directly as one liner format it like a SQL query with line breaks and indentation.
        Explain the results in a concise manner, highlighting any interesting insights or patterns in the data.
        Clear markdown response as chat message.
               """),
        ("human", "User question: {query}\n\nSQL Query Executed:\n{candidate_sql}\n\nSQL Result:\n{sql_result}")
    ])
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(FormatResponseOutput) 
    
    chain = prompt | model 
    
    response: FormatResponseOutput = chain.invoke({
        "query": query,
        "candidate_sql": candidate_sql,
        "sql_result": str(sql_result)
    })
    
    return {"messages": [AIMessage(content=response.model_dump_json(), name="format_response")]}
