from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
import os
from app.pydantic_models.node_schemas import RewriteQueryOutput , ValidateQueryOutput
from app.helpers.groq_structured import invoke_groq_structured

def rewrite_user_query(state: MessagesState) -> MessagesState:
    print(len(state["messages"]))
    print("Summary in state:", state.get("summary", ""))
    feedback_text = ""

    for msg in reversed(state["messages"]):
        print(f"Message in state: {msg.name} - {msg.content}")
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous validation failed. Feedback: {data.feedback}"
            except:
                pass
            break

    system_prompt = f"""You are an expert SQL assistant. Your task is to normalize and refine the user's question to be more accurate and efficient for finding relevant tables in the database.
    The refined query should be concise and focus on the key elements of the user's request, removing any unnecessary words or ambiguity.
    
    Make the normalized query such that writting a SQL query based on it would be straightforward and more likely to be correct on the first attempt.
   
    Make it like a direction statement for other nodes to write SQL query and find relevant tables. 
    {feedback_text}"""
    
    summary = state.get("summary", "")
    if summary:
        system_prompt += f"\n\nSummary of previous conversation:\n{summary}"

    sys_msg = SystemMessage(content=system_prompt)
    messages = state["messages"]
    
    # model = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash",
    #     google_api_key=os.getenv("GOOGLE_API_KEY"),
        
    # ).with_structured_output(RewriteQueryOutput)

    response: RewriteQueryOutput = invoke_groq_structured(
        schema_model=RewriteQueryOutput,
        messages=[sys_msg] + messages,
        model_name="openai/gpt-oss-120b",
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
    print(f"Rewritten query: {response.normalized_query}")
    return {
        "messages": [AIMessage(content=response.model_dump_json(), name="rewrite_user_query")]
    }
