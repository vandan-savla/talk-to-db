from unittest import result

from fastapi import FastAPI, HTTPException
from langchain.messages import HumanMessage
from app.main_agent import main_agent
from app.pydantic_models.response import QueryResponse
from app.pydantic_models.request import QueryRequest

app = FastAPI(title="Talk to DB", debug=True)

# @app.post("/query", response_model=QueryResponse)
@app.post("/query")
async def query_db(req: QueryRequest):
    try:
        result = await main_agent.ainvoke({"messages": [HumanMessage(content=req.question)]})
        
        # The final node is format_response, which outputs a JSON string containing answer and sql_query
        last_message = result["messages"][-1]
        
        import json
        try:
            parsed_content = json.loads(last_message.content)
            return QueryResponse(
                answer=parsed_content.get("answer", ""),
                sql_query=parsed_content.get("sql_query", "")
            )
        except json.JSONDecodeError:
            return QueryResponse(answer=last_message.content, sql_query="")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))