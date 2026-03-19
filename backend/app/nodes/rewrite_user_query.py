from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os, json
from app.pydantic_models.node_schemas import RewriteQueryOutput, ValidateQueryOutput, FormatResponseOutput

def rewrite_user_query(state: MessagesState) -> MessagesState:
    # 1. Get the latest user question
    user_question = ""
    for msg in reversed(state["messages"]):
        if msg.name == "user_query":
            user_question = msg.content
            break

    # 2. Get validation feedback if this is a retry
    feedback_text = ""
    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"\nPrevious attempt failed: {data.feedback}"
            except:
                pass
            break

    # 3. Context = summary (long term) OR last 3 exchanges (short term)
    summary = state.get("summary", "")
    if summary:
        context = f"Conversation summary:\n{summary}"
    else:
        # Build from raw messages — no LLM call, just string formatting
        lines = []
        for msg in state["messages"]:
            if msg.name == "user_query":
                lines.append(f"User: {msg.content}")
            elif msg.name == "format_response":
                try:
                    data = json.loads(msg.content)
                    lines.append(f"Assistant: {data.get('answer', '')[:200]}")
                except:
                    pass
        context = "Recent conversation:\n" + "\n".join(lines[-6:]) if lines else ""

    system_prompt = f"""You are an expert SQL assistant. Your task is to normalize and refine the user's question to be more accurate and efficient for finding relevant tables in the database.
    The refined query should be concise and focus on the key elements of the user's request, removing any unnecessary words or ambiguity.
    
    Make the normalized query such that writting a SQL query based on it would be straightforward and more likely to be correct on the first attempt.
   
    Make it like a direction statement for other nodes to write SQL query and find relevant tables. 
    {feedback_text}
    
    {context}
    Return response in JSON format given.
    
    {{"normalized_query": "..."}}

    """

    model = ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(RewriteQueryOutput, method="json_mode")

    response: RewriteQueryOutput = model.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Normalize this into JSON: {user_question}")
    ])

    print(f"Rewritten query: {response.normalized_query}")
    return {"messages": [AIMessage(content=response.model_dump_json(), name="rewrite_user_query")]}