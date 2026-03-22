import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api.services.auth.auth_routes import router as auth_routes
from api.services.conversations.conversation_routes import router as conversation_routes
from api.services.query.query_route import router as query_routes 
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

origins = [ os.getenv("FRONTEND_URL", "http://localhost:3000"), os.getenv("FRONTEND_PROD_URL") ] 
print(origins)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Talk to DB", debug=True)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(query_routes)  
app.include_router(auth_routes)
app.include_router(conversation_routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)