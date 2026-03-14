from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
import os 
from app.tools.table_schema_retrieval import get_relevant_tables
from app.pydantic_models.node_schemas import RewriteQueryOutput, TableSchemasOutput

def get_tables_schemas(state: MessagesState) -> MessagesState:
    # Extract the normalized query from the last rewrite_user_query message
    normalized_query = ""
    for msg in reversed(state["messages"]):
        if msg.name == "rewrite_user_query":
            try:
                data = RewriteQueryOutput.model_validate_json(msg.content)
                normalized_query = data.normalized_query
            except:
                pass
            break
    
    if not normalized_query:
        # Fallback to the original user question
        normalized_query = state["messages"][0].content

    # Call the tool directly since we don't need the LLM to route it
    docs = get_relevant_tables.invoke({"query": normalized_query})
    
    # Use LLM to cleanly format the response into the unified structured TableSchemasOutput
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are an expert database assistant. Based on the provided raw schema documentation, extract the actual table names and the combined schema text."),
        ("human", "User question: {query}\n\nRaw schemas: {schemas}")
    ])
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(TableSchemasOutput)

    chain = prompt | model
    
    response: TableSchemasOutput = chain.invoke({
        "query": normalized_query,
        "schemas": "\n\n".join(docs) if isinstance(docs, list) else str(docs)
    })
    
    return {"messages": [AIMessage(content=response.model_dump_json(), name="get_tables_schemas")]}