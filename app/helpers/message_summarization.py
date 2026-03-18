from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph.message import RemoveMessage
import os
from app.main_agent import main_agent

def summarize_messages_background(thread_id: str):

    config = {"configurable": {"thread_id": thread_id}}
    state = main_agent.get_state(config)
    messages = state.values.get("messages", [])
    
    # Check if there are more than 6 messages (each turn has User + AI, so history builds up)
    if len(messages) > 6:
        summary = state.values.get("summary", "")
        if summary:
            summary_message = summary
        else:
            summary_message = "No summary of conversation yet"
            
        msg = (
            "Taking into account the previous summary:\n"
            f"{summary_message}\n\n"
            "Summarize the following conversation\n"
            f"{messages}"
        )
        
        summarizePrompt = "You are tasked with summarizing the conversation betwen the user and AI.\nYour summary should be precise and captures all the details in the conversation."
        try:
            llm = ChatGroq(model="openai/gpt-oss-120b", groq_api_key=os.getenv("GROQ_API_KEY"))
            response = llm.invoke([SystemMessage(content=summarizePrompt), HumanMessage(content=msg)])
            
            # Keep the last 6 messages, remove the rest
            delete_messages = [RemoveMessage(id=m.id) for m in messages[:-6]]
            
            main_agent.update_state(config, {"summary": response.content, "messages": delete_messages})
            print(f"Background summarization completed for {thread_id}. Kept last 6 messages.")
        except Exception as e:
            print(f"Error during state update in background task: {e}")

