from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os
from app.pydantic_models.node_schemas import RewriteQueryOutput , ValidateQueryOutput

def rewrite_user_query(state: MessagesState) -> MessagesState:
    print(f"Original user query: {state} - {state['messages'][1].content}")  # Debug print to check the input state
    query = ""
    feedback_text = ""

    for msg in reversed(state["messages"]):
        print(f"Message in state: {msg.name} - {msg.content}")
        if msg.name == "user_query":
            query = msg.content
        if msg.name == "validate_query":
            try:
                data = ValidateQueryOutput.model_validate_json(msg.content)
                if not data.is_valid:
                    feedback_text = f"Previous validation failed. Feedback: {data.feedback}"
            except:
                pass
            break

    if not query:
        raise ValueError("No user query found in the state messages.")

    system_prompt = f"""You are an expert SQL assistant. Your task is to normalize and refine the user's question to be more accurate and efficient for finding relevant tables in the database.
    The refined query should be concise and focus on the key elements of the user's request, removing any unnecessary words or ambiguity.
    
    Make the normalized query such that writting a SQL query based on it would be straightforward and more likely to be correct on the first attempt.
    
    For example - query like "Can you tell me the total sales for each product category in the last quarter?" can be normalized to "Calculate total sales (sum of sales) by product category (where product category = ?)for last quarter" 
    
    Make it like a direction for other nodes to write SQL query and find relevant tables. 
    {feedback_text}"""

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        # ("system", system_prompt),
        ("human", "{query}")
    ])
    
    # model = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash",
    #     google_api_key=os.getenv("GOOGLE_API_KEY"),
        
    # ).with_structured_output(RewriteQueryOutput)


    model = ChatGroq(
        model="qwen/qwen3-32b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(RewriteQueryOutput) 
    
    chain = prompt | model
    
    response: RewriteQueryOutput = chain.invoke({"query": query})
    print(f"Rewritten query: {response.normalized_query}")
    return {
        "messages": [AIMessage(content=response.model_dump_json(), name="rewrite_user_query")]
    }