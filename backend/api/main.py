import json
from fastapi import Depends, FastAPI, HTTPException
from langchain.messages import HumanMessage
from app.main_agent import main_agent
from api.auth.auth_context import get_current_user
from api.schemas.api_schemas import LoginRequest, QueryRequest, QueryResponse, RegisterRequest
from api.auth.auth_service import login_user, register_user

app = FastAPI(title="Talk to DB", debug=True)

@app.post("/v1/query")
async def query_db(req: QueryRequest, user: dict = Depends(get_current_user)):
    try:
        result = main_agent.invoke(
            {"messages": [HumanMessage(content=req.question, name="user_query")]},
            config={"configurable": {"thread_id": req.chat_id}}
        )

        messages = result.get("messages", [])
        if not messages:
            raise HTTPException(status_code=500, detail="No response generated.")

        last = messages[-1]

        # Decider short-circuited — plain text response
        if last.name == "final_response":
            return QueryResponse(answer=last.content, sql_query="")

        # Normal pipeline — JSON response
        try:
            parsed = json.loads(last.content)
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


@app.post("/v1/auth/register")
def register(req: RegisterRequest):
    try:
        return register_user(req.email, req.password, req.full_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/v1/auth/login")
def login(req: LoginRequest):
    try:
        return login_user(req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Login failed")