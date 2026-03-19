from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os
from app.tools.table_schema_retrieval import get_relevant_tables
from app.pydantic_models.node_schemas import RewriteQueryOutput, TableSchemasOutput

def get_tables_schemas(state: MessagesState) -> MessagesState:
    normalized_query = ""
    for msg in reversed(state["messages"]):
        if msg.name == "rewrite_user_query":
            try:
                data = RewriteQueryOutput.model_validate_json(msg.content)
                normalized_query = data.normalized_query
            except:
                pass
            break

    docs = get_relevant_tables.invoke({"query": normalized_query})
    raw_schemas = "\n\n".join(docs) if isinstance(docs, list) else str(docs)

    system_prompt = f"""You are a database assistant. Extract relevant table names and schema info from the docs below.
Only include tables relevant to the question.

Raw schema docs:
{raw_schemas}

Respond ONLY with valid JSON:
{{"candidate_tables": ["table1"], "schemas_text": "..."}}
"""

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(TableSchemasOutput, method="json_mode")

    response: TableSchemasOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Extract table schemas as JSON for: {normalized_query}")
    ])

    print("Extracted schemas:", response.model_dump())
    return {"messages": [AIMessage(content=response.model_dump_json(), name="get_tables_schemas")]}