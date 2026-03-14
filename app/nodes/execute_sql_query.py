from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, List, Any, Dict
from langchain_core.messages import AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os 
from app.tools.execute_sql_query_tool import execute_sql_query

def execute_sql_query(state: BaseMessage) -> BaseMessage:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    ).bind_tools([execute_sql_query])
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant that executes the SQL query and returns the result.
        The SQL query is: {query}
        Execute the SQL query and return the result in a concise format.
        Use the Tool "execute_sql_query" to execute the SQL query and get the result.
        
        """
    )
    chain = prompt | model
    response = chain.invoke({"query": state.content})
    
    return AIMessage(content=response.content)