from pydantic import BaseModel
from typing import List, Dict, Any

class QueryResponse(BaseModel):
    answer: str
    sql_query: str
