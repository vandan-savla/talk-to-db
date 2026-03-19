from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from api.services.auth.auth_service import register_user, login_user
from api.schemas.api_schemas import LoginRequest, RegisterRequest

router = APIRouter(prefix="/v1/auth", tags=["auth"])
bearer = HTTPBearer()
from slowapi import Limiter

limiter = Limiter()


#  Routes 
@router.post("/register")
@limiter.limit("5/minute")
def register(req: RegisterRequest):
    try:
        return register_user(req.email, req.password, req.full_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login")
@limiter.limit("5/minute")
def login(req: LoginRequest):
    try:
        return login_user(req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Login failed")