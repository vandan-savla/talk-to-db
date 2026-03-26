import os
import json
import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
from app.pydantic_models.node_schemas import FormatResponseOutput, ExecuteSqlOutput, WriteSqlOutput

logger = logging.getLogger(__name__)

def format_response(state: MessagesState) -> MessagesState:
    candidate_sql, sql_result = "", []

    for msg in reversed(state["messages"]):
        if msg.name == "write_sql_query":
            try:
                candidate_sql = WriteSqlOutput.model_validate_json(msg.content).candidate_sql
            except: pass
            break

    for msg in reversed(state["messages"]):
        if msg.name == "execute_sql_query":
            try:
                sql_result = ExecuteSqlOutput.model_validate_json(msg.content).sql_result
            except: pass
            break

    logger.info("Formatting final response for user.")

    system_prompt = f"""You are a helpful database assistant. Explain the SQL result in natural language using this structure:
            1. **Result Overview**: A brief 1-2 sentence summary.
            2. **Data Table**: Use a clean Markdown table for any multi-row result.
            3. **Key insights**: 2-3 bullet points highlighting important trends or facts from the data.

            Rules:
            - ALWAYS use Markdown tables for multi-row data. 
            - Use proper markdown bolding and lists.
            - If no data was found, just state that clearly.
            - Format SQL with proper indentation.

            SQL executed:
            {candidate_sql}

            Result:
            {sql_result}

            Respond ONLY with valid JSON:
            {{"answer": "...(markdown strings)...", "sql_query": "...(formatted SQL)..."}}
        """

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(FormatResponseOutput, method="json_mode")

    response: FormatResponseOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Format the SQL result as JSON.")
    ])

    logger.debug(f"Formatted response: {response.model_dump_json()}")
    return {"messages": [AIMessage(content=response.model_dump_json(), name="format_response")]}