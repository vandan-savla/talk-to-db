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
    feedback_text= ""
    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous attempt failed: {data.feedback}"
            except: pass
            break

    system_prompt = f"""
    You are an expert SQL developer. Write an optimized SQL query with correct syntax and logic.
    Consider proper column names, table names, and SQL best practices to ensure the query runs successfully and efficiently.
    The SQL should be designed to answer the user's question as accurately as possible based on the provided schemas.

    Table schemas:
    {schemas_text}

    If any feedback is available from previous validation attempts, use it to improve the SQL: {feedback_text}
    
    If multiple queries are needed to get the final answer, write them all in the correct order. Make sure each query is correct on its own and can be executed without errors.
    
    
    Respond ONLY with valid JSON: {{"candidate_sql": ["SELECT ..."]}}
    """

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(WriteSqlOutput, method="json_mode")

    response: WriteSqlOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Write the SQL query as JSON for: {normalized_query}")
    ])

    logger.info(f"Generated SQL query: {response.candidate_sql}...")
    return {"messages": [AIMessage(content=response.model_dump_json(), name="write_sql_query")]}