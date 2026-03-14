from pydantic import BaseModel, Field
from typing import List, Dict, Any

class RewriteQueryOutput(BaseModel):
    normalized_query: str = Field(description="The refined and normalized user query for table schema retrieval.")

class TableSchemasOutput(BaseModel):
    schemas_text: str = Field(description="The retrieved schemas of the relevant tables as a formatted string.")
    candidate_tables: List[str] = Field(description="List of candidate table names.")

class WriteSqlOutput(BaseModel):
    candidate_sql: str = Field(description="The generated SQL query.")

class ValidateQueryOutput(BaseModel):
    is_valid: bool = Field(description="True if the SQL query correctly answers the user's question, False otherwise.")
    feedback: str = Field(description="Feedback on why the query is invalid. Leave empty if the query is valid.")

class AnswerOutput(BaseModel):
    answer: str = Field(description="The natural language answer based on the SQL result.")

class ExecuteSqlOutput(BaseModel):
    sql_result: List[Dict[str, Any]] = Field(description="The raw execution result rows from the database.")
    answer: str = Field(description="The natural language answer based on the SQL result.")
