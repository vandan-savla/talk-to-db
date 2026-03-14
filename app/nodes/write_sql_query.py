from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, List, Any, Dict
from langchain_core.messages import AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os 

def get_tables_schemas(state: BaseMessage) -> BaseMessage:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant that writes the SQL query based on the user's question and the relevant table schemas.
        
        The user's question is: {query}
        Write a SQL query to answer the user's question based on the relevant table schemas.
        {schemas_text}
        """
    )
    chain = prompt | model
    response = chain.invoke({"query": state.content, "schemas_text": state.schemas_text})
    
    return AIMessage(content=response.content)