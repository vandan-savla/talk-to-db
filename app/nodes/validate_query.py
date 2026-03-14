from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import TypedDict, List, Any, Dict
from langchain_core.messages import AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os 

def validate_query(state: BaseMessage) -> BaseMessage:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant that validates the SQL query based on the user's question and the relevant table schemas.
        
        The user's question is: {query}
        The SQL query is: {candidate_sql}
        Validate if the SQL query correctly answers the user's question based on the relevant table schemas.
        Return "valid" if the SQL query is valid, otherwise return "invalid".
        """
    )
    chain = prompt | model
    response = chain.invoke({"query": state.content, "candidate_sql": state.candidate_sql})
    
    is_valid = response.content.strip().lower() == "valid"
    
    return AIMessage(content=str(is_valid))