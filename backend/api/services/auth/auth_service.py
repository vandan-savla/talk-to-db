import os
import warnings
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from jose import JWTError, jwt
from utils.connect import connect_to_app_db     
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends

bearer = HTTPBearer()

warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")

load_dotenv()

# ── Config ────────────────────────────────────────────────────
JWT_SECRET      = os.getenv("JWT_SECRET")
JWT_ALGORITHM   = "HS256"
JWT_EXPIRY_DAYS = 7

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── JWT helpers ───────────────────────────────────────────────
def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError(str(e))


# ── Register ──────────────────────────────────────────────────
def register_user(email: str, password: str, full_name: str = None) -> dict:
    # Validate password length (bcrypt hard limit is 72 bytes)
    # if not password or len(password.encode("utf-8")) > 72:
    #     raise ValueError("Password must be between 1 and 72 characters")

    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                raise ValueError("Email already registered")

            cur.execute(
                """
                INSERT INTO users (email, password_hash, full_name)
                VALUES (%s, %s, %s)
                RETURNING id, email, full_name
                """,
                (email, hash_password(password), full_name)
            )
            user = dict(cur.fetchone())
            conn.commit()

        return {
            "access_token": create_token(str(user["id"]), user["email"]),
            "token_type": "bearer",
            "user": {
                "id":        str(user["id"]),
                "email":     user["email"],
                "full_name": user["full_name"],
            }
        }
    except ValueError:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"[register_user] Unexpected error: {e}")
        raise ValueError("Registration failed. Please try again.")
    finally:
        conn.close()


# ── Login ─────────────────────────────────────────────────────
def login_user(email: str, password: str) -> dict:
    # if not password or len(password.encode("utf-8")) > 72:
    #     raise ValueError("Invalid email or password")

    conn = connect_to_app_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, full_name, password_hash FROM users WHERE email = %s",
                (email,)
            )
            row = cur.fetchone()

            if not row or not verify_password(password, row["password_hash"]):
                raise ValueError("Invalid email or password")

            user = dict(row)

        return {
            "access_token": create_token(str(user["id"]), user["email"]),
            "token_type": "bearer",
            "user": {
                "id":        str(user["id"]),
                "email":     user["email"],
                "full_name": user["full_name"],
            }
        }
    except ValueError:
        raise
    except Exception as e:
        print(f"[login_user] Unexpected error: {e}")
        raise ValueError("Login failed. Please try again.")
    finally:
        conn.close()
        

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    try:
        return decode_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))