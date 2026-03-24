import os
import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
from app.pydantic_models.node_schemas import RewriteQueryOutput, WriteSqlOutput, TableSchemasOutput, ValidateQueryOutput

logger = logging.getLogger(__name__)

def write_sql_query(state: MessagesState) -> MessagesState:
    # 1. Get the latest normalized query
    normalized_query = ""
    for msg in reversed(state["messages"]):
        if msg.name == "get_tables_schemas":
            try:
                schemas_text = TableSchemasOutput.model_validate_json(msg.content).schemas_text
            except: pass
            break

    for msg in reversed(state["messages"]):
        if msg.name == "rewrite_user_query":
            try:
                normalized_query = RewriteQueryOutput.model_validate_json(msg.content).normalized_query
            except:
                pass
            break
            
    # 2. Get the table schemas
    schemas_text = ""
    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous attempt failed: {data.feedback}"
            except: pass
            break

    logger.info(f"Writing SQL for normalized query: {normalized_query[:50]}...")

    system_prompt = f"""You are a PostgreSQL expert. Write a syntactically correct SQL query based on the following:
    Normalized User Request: {normalized_query}
    
    Table Schemas:
    {schemas_text}
    
    RULES:
    1. Only use the tables and columns provided in the schemas.
    2. The query must be a valid SELECT statement.
    3. Return ONLY the JSON requested.
    
    {{"candidate_sql": "SELECT ..."}}
    """

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(WriteSqlOutput, method="json_mode")

    response: WriteSqlOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Write the SQL query as JSON for: {normalized_query}")
    ])

    logger.info(f"Generated SQL query: {response.candidate_sql[:100]}...")
    return {"messages": [AIMessage(content=response.model_dump_json(), name="write_sql_query")]}