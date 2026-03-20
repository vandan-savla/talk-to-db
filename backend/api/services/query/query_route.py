import json
from fastapi import APIRouter, Depends, HTTPException, Request
from langchain.messages import HumanMessage
from langchain_core.messages import BaseMessage
from app.main_agent import main_agent
from api.schemas.api_schemas import QueryRequest, QueryResponse
from api.services.auth.auth_service import get_current_user
from api.services.conversations.conversation_service import save_messages
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.tools.execute_sql_query_tool import execute_sql_query
from utils.connect import connect_to_master_db, connect_to_app_db
limiter = Limiter(key_func=get_remote_address)  # global rate limit for simplicity

router = APIRouter(prefix="/v1", tags=["query to master db"])


@router.post("/query")
@limiter.limit("10/second")
async def query_db(request: Request, req: QueryRequest, user: dict = Depends(get_current_user)):
    try:
        result = main_agent.invoke(
            {"messages": [HumanMessage(content=req.question, name="user_query")]},
            config={"configurable": {"thread_id": req.conversation_id}}
        )

        messages = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No response generated.")

        last : BaseMessage = messages[-1]

        # Decider short-circuited — plain text response
        if last.name == "final_response":
            return QueryResponse(answer=last.content, sql_query="")

        # Normal pipeline — JSON response
        try:
            parsed: dict = json.loads(last.content)
            if parsed:
                save_messages(
                    conversation_id=req.conversation_id,
                    user_question=req.question,
                    answer=parsed.get("answer", ""),
                    sql_query=parsed.get("sql_query", "")
                )
            
            return QueryResponse(
                answer=parsed.get("answer", ""),
                sql_query=parsed.get("sql_query", "")
            )
        except json.JSONDecodeError:
            return QueryResponse(answer=last.content, sql_query="")

    except HTTPException:
        raise  # re-raise FastAPI errors as-is
    except Exception as e:
        print(f"[query_db] Unhandled error: {e}")  # log internally
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again."  # never expose internals
        )


@router.post("/explorer/query")
@limiter.limit("5/second")
def explorer_query(request: Request, req: dict, user: dict = Depends(get_current_user)):
    sql = req.get("sql", "").strip()
    if not sql.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries allowed")
    result = execute_sql_query(sql)
    return {"rows": result}


@router.get("/explorer/schema")
def get_schema(request: Request, user: dict = Depends(get_current_user)):
    """Fetches table schemas and relationships from JSON artifacts instead of the DB."""
    import os
    from pathlib import Path

    # Base directory for artifacts
    base_path = Path("e:/Codes/AI/talk to db/backend/.artifacts/public")
    if not base_path.exists():
        # Fallback if the above path is not found (e.g. running from a different context)
        base_path = Path(".artifacts/public")

    columns_res = []
    relationships_res = []

    if not base_path.exists():
        return {"columns": [], "relationships": []}

    try:
        # Iterate through table directories
        for table_dir in base_path.iterdir():
            if not table_dir.is_dir():
                continue
            
            # Find the latest artifact JSON for this table
            artifacts = sorted(list(table_dir.glob("artifact_*.json")), reverse=True)
            if not artifacts:
                continue
            
            latest_file = artifacts[0]
            with open(latest_file, "r") as f:
                data = json.load(f)
                
                table_name = data.get("table_name", table_dir.name)
                
                # Parse columns
                for col in data.get("columns", []):
                    c_name = col.get("name")
                    c_type = col.get("type", "unknown")
                    c_desc = col.get("description", "").lower()
                    is_pk = "primary key" in c_desc or c_name == f"{table_name}_id"
                    
                    columns_res.append([table_name, c_name, c_type, is_pk])
                
                # Parse relationships
                for rel in data.get("relationships", []):
                    relationships_res.append([
                        table_name,
                        rel.get("column"),
                        rel.get("references_table"),
                        rel.get("references_column")
                    ])
                    
        return {
            "columns": columns_res,
            "relationships": relationships_res
        }
    except Exception as e:
        print(f"[get_schema] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
