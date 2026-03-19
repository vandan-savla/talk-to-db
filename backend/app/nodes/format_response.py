from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os
from app.pydantic_models.node_schemas import FormatResponseOutput, ExecuteSqlOutput, WriteSqlOutput

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

    system_prompt = f"""You are a helpful database assistant. Explain the SQL result in natural language.
            - Use markdown tables for multi-row results
            - Format SQL with proper indentation
            - Be concise but highlight key insights

            SQL executed:
            {candidate_sql}

            Result:
            {sql_result}

            Respond ONLY with valid JSON:
            {{"answer": "...(markdown)...", "sql_query": "...(formatted SQL)..."}}
        """

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(FormatResponseOutput, method="json_mode")

    response: FormatResponseOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content="Format the SQL result as JSON.")
    ])

    print("Formatted response:", response.model_dump())
    return {"messages": [AIMessage(content=response.model_dump_json(), name="format_response")]}