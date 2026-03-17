from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import MessagesState
import os
from app.pydantic_models.node_schemas import DeciderOutput
from langchain_core.messages import HumanMessage


def get_last_user_message(messages):
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def decider_node(state: MessagesState) -> MessagesState:

    query = get_last_user_message(state["messages"])
    print("Decider input:", query)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a classifier.

Return:
- decision = true → if DB query needed
- decision = false → if greeting / small talk

If false → also generate a direct response.
"""),
        ("human", "{query}")
    ])

    # model = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash-lite",
    #     google_api_key=os.getenv("GOOGLE_API_KEY"),
    #     max_output_tokens=100,
    #     temperature=0
    # ).with_structured_output(DeciderOutput)

    model = ChatGroq(
        model="qwen/qwen3-32b",
        groq_api_key=os.getenv("GROQ_API_KEY")
    ).with_structured_output(DeciderOutput) 
    

    response: DeciderOutput = (prompt | model).invoke({"query": query})

    # 🔥 KEY PART
    if not response.decision:
        return {
            "messages": [
                AIMessage(
                    content=response.response,
                    name="final_response"
                )
            ]
        }

    # else → continue pipeline
    return {
        "messages": [
            AIMessage(
                content=response.model_dump_json(),
                name="decider_node"
            )
        ]
    }