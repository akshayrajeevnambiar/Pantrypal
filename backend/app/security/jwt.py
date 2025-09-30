# app/security/jwt.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import os
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env file

SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me") 
ALGORITHM = os.getenv("JWT_ALG", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MIN", "60"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Build a signed JWT containing `data` plus standard claims.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Standard claims
    to_encode.update({"iat": now, "exp": expire})
    # Sign & return compact JWT
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    """
    Verify signature & expiration; return payload dict or raise JWTError.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise e
