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
    """Fetches table schemas and relationships for the ERD."""
    conn = connect_to_master_db()
    if not conn:
        raise HTTPException(status_code=500, detail="Could not connect to master database")
    
    try:
        with conn.cursor() as cur:
            # Get tables and columns
            cur.execute("""
                SELECT 
                    t.table_name, 
                    c.column_name, 
                    c.data_type,
                    CASE WHEN cu.column_name IS NOT NULL THEN TRUE ELSE FALSE END as is_primary
                FROM 
                    information_schema.tables t
                JOIN 
                    information_schema.columns c ON t.table_name = c.table_name
                LEFT JOIN 
                    information_schema.key_column_usage cu ON t.table_name = cu.table_name 
                    AND c.column_name = cu.column_name
                    AND cu.constraint_name IN (
                        SELECT constraint_name 
                        FROM information_schema.table_constraints 
                        WHERE constraint_type = 'PRIMARY KEY'
                    )
                WHERE 
                    t.table_schema = 'public'
                ORDER BY 
                    t.table_name, c.ordinal_position;
            """)
            columns = cur.fetchall()
            
            # Get foreign keys for relationships
            cur.execute("""
                SELECT
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='public';
            """)
            relationships = cur.fetchall()
            
            return {
                "columns": columns,
                "relationships": relationships
            }
    except Exception as e:
        print(f"[get_schema] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()