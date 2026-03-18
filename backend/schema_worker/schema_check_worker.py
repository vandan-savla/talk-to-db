from .generate_table_artifact import generate_table_artifacts
from vector_store.qdrant_store import vector_store
from vector_store.build_documents import build_schema_documents
from qdrant_client.models import PointStruct
import uuid


def table_to_uuid(schema: str, table: str) -> str:
    name = f"{schema}.{table}"
    return (uuid.uuid5(uuid.NAMESPACE_DNS, name))


def upsert_schema():

    db_structure = generate_table_artifacts()

    docs = build_schema_documents(db_structure)

    embeddings = vector_store.embeddings

    points = []

    for doc in docs:
        schema = doc.metadata["schema"]
        table_name = doc.metadata["table_name"]
        
       
        vector = embeddings.embed_documents([doc.page_content])[0]
        vector_id  = table_to_uuid(schema, table_name)
        print(f"Upserting vector for {schema}.{table_name} with id {vector_id}")
        
        points.append(
            PointStruct(
                id=vector_id,
                vector=vector,
                payload={
                    "page_content": doc.page_content,
                    "metadata": doc.metadata                
                }
            )
        )
    
    vector_store.client.upsert(
        collection_name=vector_store.collection_name,
        points=points
    )

    print(f"Upserted {len(points)} schema vectors")
    
if __name__ == "__main__":
    upsert_schema()