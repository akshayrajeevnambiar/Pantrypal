# app/security/deps.py
from typing import Callable, Iterable, List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.orm import SessionLocal
from app.models.users import User
from app.security.jwt import decode_token

# Re-usable HTTP Bearer parser (looks for Authorization: Bearer <token>)
bearer_scheme = HTTPBearer(auto_error=False)

def get_db():
    """
    Dependency that yields a DB session per request and closes it afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract & verify the Bearer token, decode JWT, load User from DB, ensure active.
    Raises 401 if token missing/invalid/expired or user not active.
    """
    if creds is None or creds.scheme.lower() != "bearer":
        # No/malformed Authorization header
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate & decode the token (will raise if invalid/expired)
    try:
        payload = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 'sub' (subject) should be the user id we encoded during login
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Load user from DB and ensure active
    user = db.get(User, int(user_id))
    if not user or not user.is_active:
        # Don't leak which part failed (treat as unauthorized)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_roles(*allowed_roles: str) -> Callable[[User], User]:
    """
    Factory that returns a dependency enforcing that current_user.role is allowed.
    Usage:
        @router.post("/something")
        def handler(current_user: User = Depends(require_roles("admin","manager"))):
            ...
    """
    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            # Authenticated but not permitted
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )
        return current_user

    return _dep
