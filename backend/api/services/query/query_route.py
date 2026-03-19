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
