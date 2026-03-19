from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from api.services.auth.auth_service import register_user, login_user
from api.schemas.api_schemas import LoginRequest, RegisterRequest
from slowapi.util import get_remote_address
from slowapi import Limiter

router = APIRouter(prefix="/v1/auth", tags=["auth"])
bearer = HTTPBearer()

limiter = Limiter(key_func=get_remote_address)

#  Routes 
@router.post("/register")
@limiter.limit("10/second")
def register(request: Request, req: RegisterRequest):
    try:
        return register_user(req.email, req.password, req.full_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
@limiter.limit("10/second")
def login(request: Request, req: LoginRequest):
    try:
        return login_user(req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Login failed")