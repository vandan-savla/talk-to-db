from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import MessagesState
import os 
from app.pydantic_models.node_schemas import TableSchemasOutput, WriteSqlOutput, ValidateQueryOutput

def validate_query(state: MessagesState) -> MessagesState:
    schemas_text = ""
    candidate_sql = ""
    
    for msg in reversed(state["messages"]):
        if msg.name == "get_tables_schemas" and not schemas_text:
            try:
                data = TableSchemasOutput.model_validate_json(msg.content)
                schemas_text = data.schemas_text
            except:
                pass
        elif msg.name == "write_sql_query" and not candidate_sql:
            try:
                data = WriteSqlOutput.model_validate_json(msg.content)
                candidate_sql = data.candidate_sql
            except:
                pass
                
        if schemas_text and candidate_sql:
            break

    query = state["messages"][0].content

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert SQL validator. Validate if the given SQL query correctly answers the user's question based on the provided table schemas. If it is invalid, provide specific feedback on what is wrong and how to fix it."),

        ("human", "User question: {query}\n\nTable schemas:\n{schemas}\n\nCandidate SQL:\n{candidate_sql}")
    ])
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(ValidateQueryOutput)
    
    chain = prompt | model
    
    response: ValidateQueryOutput = chain.invoke({
        "query": query,
        "schemas": schemas_text,
        "candidate_sql": candidate_sql
    })
    
    return {"messages": [AIMessage(content=response.model_dump_json(), name="validate_query")]}