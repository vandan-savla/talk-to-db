from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.main_agent import AgentState

def write_sql_query(state: AgentState) -> AgentState:
    prompt = ChatPromptTemplate.from_template(
        """ 
        You are a helpful assistant that writes SQL queries to answer the user's question.
        You need to refine the query to be more accurate and efficient.

        The user's query is: {query}

        Return the normalized user query. So it can be used in retrieval process to find relavant tables.
        """
    )
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    chain = prompt | model | StrOutputParser()
    result = chain.invoke(state["query"])
    return {"normalized_query": result}