from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os 
from app.pydantic_models.node_schemas import RewriteQueryOutput, TableSchemasOutput, WriteSqlOutput
from app.pydantic_models.node_schemas import ValidateQueryOutput

def write_sql_query(state: MessagesState) -> MessagesState:
    schemas_text = ""
    print("State in write_sql_query node:", state["messages"][1].content) 
    for msg in reversed(state["messages"]):
        if msg.name == "get_tables_schemas":
            try:
                data = TableSchemasOutput.model_validate_json(msg.content)
                print( "Data -" ,data.model_dump())
                schemas_text = data.schemas_text
            except:
                pass
            break
    normalized_query = ""
    for msg in reversed(state["messages"]):
        if msg.name == "rewrite_user_query":
            try:
                data = RewriteQueryOutput.model_validate_json(msg.content)
                print( "Data -" ,data.model_dump())
                normalized_query = data.normalized_query
                if not normalized_query:
                    normalized_query = state["messages"][-1].content
            except:
                pass
            break
    
    feedback_text = ""
    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous attempt failed. Feedback: {data.feedback}"
            except:
                pass
            break
            
    system_prompt = f"""You are an expert SQL developer. Write a Optimized SQL query to answer the user's question based on the provided table schemas. Return only the SQL query.
    The SQL query should be accurate and efficient, utilizing the relevant tables and columns from the provided schemas. 
    Dont write the unoptimized query, write the optimized version of the query directly. As the load on the database is high, we want to make sure the SQL query is as efficient as possible to reduce execution time and resource usage.
    
    Make sure to write SQL query without any special formatting like markdown or code blocks, just the plain SQL query following the output schema.
    
    {feedback_text}"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        ("human", "User question: {normalized_query}\n\nTable schemas:\n{schemas_text}")
    ])
    
    # model = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash-lite",
    #     google_api_key=os.getenv("GOOGLE_API_KEY")
    # ).with_structured_output(WriteSqlOutput)
    
    
    model = ChatGroq(
        model="qwen/qwen3-32b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(WriteSqlOutput) 
    
    chain = prompt | model
    
    response: WriteSqlOutput = chain.invoke({
        "normalized_query": normalized_query,
        "schemas_text": schemas_text
    })
    
    return {"messages": [AIMessage(content=response.model_dump_json(), name="write_sql_query")]}