from pydantic import BaseModel
from typing import List, Dict, Any

class QueryRequest(BaseModel):
    question: str
    chat_id: str
    
    
class QueryResponse(BaseModel):
    answer: str
    sql_query: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    
class LoginRequest(BaseModel):
    email: str
    password: str
    