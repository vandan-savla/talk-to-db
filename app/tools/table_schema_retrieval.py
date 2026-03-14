from typing import List
from langchain_community.embeddings import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
)

collection_name="schema_vectors"
vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=collection_name,
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

@tool("get_relevant_tables", return_direct=True)
def get_relevant_tables(query: str) -> List[str]:
    """
    Get the relevant tables for the given normalized query.
    """
    docs = vector_store.similarity_search(query, k=5)
    # return docs
    return [doc.page_content for doc in docs]
