from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
import os
from app.pydantic_models.node_schemas import RewriteQueryOutput , ValidateQueryOutput

def rewrite_user_query(state: MessagesState) -> MessagesState:
    print(f"Original user query: {state} - {state['messages'][0].content}")
    query = state["messages"][0].content
    feedback_text = ""
    for msg in reversed(state["messages"]):
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous validation failed. Feedback: {data.feedback}"
            except:
                pass
            break

    system_prompt = f"""You are an expert SQL assistant. Your task is to normalize and refine the user's question to be more accurate and efficient for finding relevant tables in the database.
    {feedback_text}"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        # ("system", system_prompt),
        ("human", "{query}")
    ])
    
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(RewriteQueryOutput)

    chain = prompt | model
    
    response: RewriteQueryOutput = chain.invoke({"query": query})

    return {
        "messages": [AIMessage(content=response.model_dump_json(), name="rewrite_user_query")]
    }