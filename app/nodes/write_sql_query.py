from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import MessagesState
import os 
from app.pydantic_models.node_schemas import TableSchemasOutput, WriteSqlOutput
from app.pydantic_models.node_schemas import ValidateQueryOutput

def write_sql_query(state: MessagesState) -> MessagesState:
    schemas_text = ""
    for msg in reversed(state["messages"]):
        if msg.name == "get_tables_schemas":
            try:
                data = TableSchemasOutput.model_validate_json(msg.content)
                schemas_text = data.schemas_text
            except:
                pass
            break
            
    query = state["messages"][0].content
    
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
            
    system_prompt = f"""You are an expert SQL developer. Write a SQL query to answer the user's question based on the provided table schemas. Return only the SQL query.
    {feedback_text}"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        ("human", "User question: {query}\n\nTable schemas:\n{schemas_text}")
    ])
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(WriteSqlOutput)
    
    chain = prompt | model
    
    response: WriteSqlOutput = chain.invoke({
        "query": query,
        "schemas_text": schemas_text
    })
    
    return {"messages": [AIMessage(content=response.model_dump_json(), name="write_sql_query")]}