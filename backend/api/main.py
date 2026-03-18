from langchain_core.messages import BaseMessage
from fastapi import FastAPI, HTTPException, BackgroundTasks
from langchain.messages import HumanMessage
from app.main_agent import main_agent
from app.helpers.message_summarization import summarize_messages_background
from app.pydantic_models.response import QueryResponse
from app.pydantic_models.request import QueryRequest

app = FastAPI(title="Talk to DB", debug=True)

# @app.post("/query", response_model=QueryResponse)
@app.post("/query")
async def query_db(req: QueryRequest, background_tasks: BackgroundTasks):
    try:
        # result = await main_agent.ainvoke({"messages": [HumanMessage(content=req.question)]}, config={"configurable": {"thread_id": req.chat_id}})
        result = main_agent.invoke({"messages": [HumanMessage(content=req.question, name="user_query")]}, config={"configurable": {"thread_id": req.chat_id}})
        
        # Schedule the background summarization task
        background_tasks.add_task(summarize_messages_background, req.chat_id)
        
        # The final node is format_response, which outputs a JSON string containing answer and sql_query
        result_messages = result.get("messages", [])
        if not result_messages:
            raise HTTPException(status_code=500, detail="Agent returned no messages.")

        last_message: BaseMessage = result_messages[-1]
        
        import json
        try:
            parsed_content: dict = json.loads(last_message.content)
            return QueryResponse(
                answer=parsed_content.get("answer", ""),
                sql_query=parsed_content.get("sql_query", "")
            )
        except json.JSONDecodeError:
            return QueryResponse(answer=last_message.content, sql_query="")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
