from typing import List
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY"),
)

def get_relevant_tables(normalized_query: str) -> List[str]:
    """
    Get the relevant tables for the given normalized query.
    """
    