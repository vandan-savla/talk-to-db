from fastapi import APIRouter, HTTPException, Depends, Request
from api.services.auth.auth_service import get_current_user
from api.services.conversations.conversation_service import (
    create_conversation,
    get_conversations,
    get_messages,
    get_conversation_by_id
)
from api.schemas.api_schemas import ConversationCreateSchema
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/v1/conversations", tags=["conversations"])


# ── Create new conversation ───────────────────────────────────
@limiter.limit("10/minute")
@router.post("")
def new_conversation(request: Request,req:ConversationCreateSchema , user: dict = Depends(get_current_user)):
    try:
        
        return create_conversation(user_id=user["sub"], title=req.title or "Untitled Conversation")
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