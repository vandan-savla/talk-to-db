import json
from fastapi import FastAPI, HTTPException
from langchain.messages import HumanMessage
from app.main_agent import main_agent
from app.pydantic_models.response import QueryResponse
from app.pydantic_models.request import QueryRequest

app = FastAPI(title="Talk to DB", debug=True)

@app.post("/query")
async def query_db(req: QueryRequest):
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
