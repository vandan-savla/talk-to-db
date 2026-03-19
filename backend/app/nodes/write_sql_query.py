from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os
from app.pydantic_models.node_schemas import RewriteQueryOutput, TableSchemasOutput, WriteSqlOutput, ValidateQueryOutput

def write_sql_query(state: MessagesState) -> MessagesState:
    schemas_text, normalized_query, feedback_text = "", "", ""

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
            except: pass
            break

    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous attempt failed: {data.feedback}"
            except: pass
            break

    system_prompt = f"""You are an expert SQL developer. Write an optimized SQL query.

Table schemas:
{schemas_text}

{f"Feedback: {feedback_text}" if feedback_text else ""}

Respond ONLY with valid JSON: {{"candidate_sql": "SELECT ..."}}
"""

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(WriteSqlOutput, method="json_mode")

    response: WriteSqlOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Write the SQL query as JSON for: {normalized_query}")
    ])

    print(f"Generated SQL: {response.candidate_sql}")
    return {"messages": [AIMessage(content=response.model_dump_json(), name="write_sql_query")]}