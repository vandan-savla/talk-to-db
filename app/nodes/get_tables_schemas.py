from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, List, Any, Dict
from langchain_core.messages import AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os 
from app.tools.table_schema_retrieval import get_relevant_tables

def get_tables_schemas(state: BaseMessage) -> BaseMessage:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    ).bind_tools([get_relevant_tables])    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant that retrieves relevant table schemas based on the user's question.

        The user's normalized query is: {query}

        Use the tool "get_relevant_tables" to get context of the relevant tables and their schemas. 
        Return the relevant tables and their schemas in a concise format.
        """
    )
    
    chain = prompt | model
    response = chain.invoke({"query": state.content})
    
    return AIMessage(content=response.content)