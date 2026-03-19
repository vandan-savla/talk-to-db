import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.services.auth.auth_routes import router as auth_routes
from api.services.conversations.conversation_routes import router as conversation_routes
from api.services.query.query_route import router as query_route 
from dotenv import load_dotenv
load_dotenv

origins = [ os.getenv("FRONTEND_URL", "http://localhost:3000"), os.getenv("FRONTEND_PROD_URL") ]  # allow env var override, default to 


app = FastAPI(title="Talk to DB", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["GET, POST"],
    allow_headers=["*"]
)
app.include_router(query_route)  
app.include_router(auth_routes)
app.include_router(conversation_routes)

