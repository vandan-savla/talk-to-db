from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import MessagesState
import os 
from app.pydantic_models.node_schemas import RewriteQueryOutput, TableSchemasOutput, WriteSqlOutput
from app.pydantic_models.node_schemas import ValidateQueryOutput
from app.helpers.groq_structured import invoke_groq_structured

def write_sql_query(state: MessagesState) -> MessagesState:
    schemas_text = ""
    latest_message = state["messages"][-1].content if state.get("messages") else ""
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
                    normalized_query = latest_message
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
            
    system_prompt = f"""You are an expert SQL developer. Write a Optimized SQL query to answer the user's question based on the provided table schemas. 
    Return the output according to the provided schema.
    
    The SQL query should be accurate and efficient, utilizing the relevant tables and columns from the provided schemas. 
    Dont write the unoptimized query, write the optimized version of the query directly. As the load on the database is high, we want to make sure the SQL query is as efficient as possible to reduce execution time and resource usage.
    The normalized query is juyst to give you better context of the user's question, it is not the query to be followed exactly , just take reference. 
    
    Feedback - {feedback_text}
    
    Table schemas:
    {schemas_text}
    
    Note: A normalized query based on the latest question is provided below for better context:
    Normalized query: {normalized_query}
    """

    summary = state.get("summary", "")
    if summary:
        system_prompt += f"\n\nSummary of previous conversation:\n{summary}"

    sys_msg = SystemMessage(content=system_prompt)
    messages = state["messages"]

    # model = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash-lite",
    #     google_api_key=os.getenv("GOOGLE_API_KEY")
    # ).with_structured_output(WriteSqlOutput)
    
    
    response: WriteSqlOutput = invoke_groq_structured(
        schema_model=WriteSqlOutput,
        messages=[sys_msg] + messages,
        model_name="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    
    return {"messages": [AIMessage(content=response.model_dump_json(), name="write_sql_query")]}
