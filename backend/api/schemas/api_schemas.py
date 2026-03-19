from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    question: str
    conversation_id: str  
    
    
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
    
class ConversationCreateSchema(BaseModel):
    title: Optional[str]