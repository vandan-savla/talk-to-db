from fastapi import FastAPI, HTTPException
from app.main_agent import main_agent
from app.pydantic_models.response import QueryResponse
from app.pydantic_models.request import QueryRequest

app = FastAPI(title="Talk to DB", debug=True)

@app.post("/query", response_model=QueryResponse)
async def query_db(req: QueryRequest):
    try:
        result = await main_agent.ainvoke({"query": req.question})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))