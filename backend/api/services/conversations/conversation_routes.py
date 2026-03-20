from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, Body
from api.services.auth.auth_service import get_current_user
from api.services.conversations.conversation_service import (
    create_conversation,
    get_conversations,
    delete_conversation,
    get_messages,
    get_conversation_by_id,
    update_conversation_title
)
from api.schemas.api_schemas import ConversationCreateSchema
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/v1/conversations", tags=["conversations"])


# ── Create new conversation ───────────────────────────────────
@limiter.limit("10/minute")
@router.post("")
def new_conversation(request: Request, req: Optional[ConversationCreateSchema] = None, user: dict = Depends(get_current_user)):
    try:
        title = req.title if req else "Untitled Conversation"
        return create_conversation(user_id=user["sub"], title=title or "Untitled Conversation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── List all conversations for current user ───────────────────
@router.get("")
def list_conversations(request: Request,user: dict = Depends(get_current_user)):
    try:
        return get_conversations(user_id=user["sub"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Get messages for a conversation ──────────────────────────
@router.get("/{conversation_id}/messages")
def list_messages(request: Request, conversation_id: str, user: dict = Depends(get_current_user)):
    try:
        convo = get_conversation_by_id(conversation_id)
        if not convo or str(convo["user_id"]) != user["sub"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return get_messages(conversation_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Update conversation title ─────────────────────────────
@router.patch("/{conversation_id}")
def update_title(request: Request, conversation_id: str, req: Optional[ConversationCreateSchema] = None, user: dict = Depends(get_current_user)):
    try:
        convo = get_conversation_by_id(conversation_id)
        if not convo or str(convo["user_id"]) != user["sub"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        title = req.title if req else None
        if not title:
            raise HTTPException(status_code=400, detail="Title is required")
            
        update_conversation_title(conversation_id, title)
        return {"id": conversation_id, "title": title}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Delete conversation ───────────────────────────────────────
@router.delete("/{conversation_id}")
def delete_convo(request: Request, conversation_id: str, user: dict = Depends(get_current_user)):
    try:
        convo = get_conversation_by_id(conversation_id)
        if not convo or str(convo["user_id"]) != user["sub"]:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        delete_conversation(conversation_id)
        return {"status": "deleted", "id": conversation_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))