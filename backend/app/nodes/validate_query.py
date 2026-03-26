import os
import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
from app.pydantic_models.node_schemas import RewriteQueryOutput, TableSchemasOutput, WriteSqlOutput, ValidateQueryOutput

logger = logging.getLogger(__name__)

def validate_query(state: MessagesState) -> MessagesState:
    schemas_text, candidate_sql, normalized_query = "", "", ""

    for msg in reversed(state["messages"]):
        if msg.name == "get_tables_schemas":
            try:
                schemas_text = TableSchemasOutput.model_validate_json(msg.content).schemas_text
            except: pass
            break

    for msg in reversed(state["messages"]):
        if msg.name == "write_sql_query":
            try:
                candidate_sql = WriteSqlOutput.model_validate_json(msg.content).candidate_sql
            except: pass
            break

    for msg in reversed(state["messages"]):
        if msg.name == "rewrite_user_query":
            try:
                normalized_query = RewriteQueryOutput.model_validate_json(msg.content).normalized_query
            except: pass
            break

    logger.info(f"Validating SQL for query: {normalized_query[:50]}...")

    system_prompt = f"""You are an expert SQL validator. Check if the SQL correctly answers the question given the schema.
        Verify syntax, table names, column names, and logic.
        Also understand shortcuts, context and implicit info in the question to validate if the SQL is likely to return the correct answer, not just if it's syntactically correct.
        
        Table schemas:
        {schemas_text}

        SQL to validate:
        {candidate_sql}

        Respond ONLY with valid JSON: {{"is_valid": true/false, "feedback": "..."}}
        """

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(ValidateQueryOutput, method="json_mode")

    response: ValidateQueryOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Validate this SQL as JSON for question: {normalized_query}")
    ])

    logger.info(f"Validation result: {response.is_valid}")

    return {"messages": [AIMessage(content=response.model_dump_json(), name="validate_query")]}