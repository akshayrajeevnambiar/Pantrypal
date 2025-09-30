# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, TokenResponse
from app.security.passwords import verify_password
from app.security.jwt import create_access_token
from app.core.orm import SessionLocal
from app.models.users import User

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    """
    Dependency that yields a SQLAlchemy session and ensures it's closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Verify email & password; return a JWT with user id & role.
    """
    # 1) Find user by email
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 2) Verify password hash
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 3) Build token payload — minimal & useful
    token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})

    return TokenResponse(access_token=token)
