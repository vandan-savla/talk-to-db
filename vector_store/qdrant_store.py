import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
)

collection_name="schema_vectors"
print(client.collection_exists(collection_name))

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=len(embeddings.embed_query("test")), distance=Distance.COSINE)
    )

vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=collection_name,
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)