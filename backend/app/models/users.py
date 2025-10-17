# backend/app/models/users.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from app.core.orm import Base

class User(Base):
    __tablename__ = "users"

    # Primary key column (integer, auto-increment)
    id: Mapped[int] = mapped_column(primary_key=True)

    # Unique login identity
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Display name
    name: Mapped[str] = mapped_column(String(120))

    # Role for RBAC (admin | manager | counter)
    role: Mapped[str] = mapped_column(String(20), default="counter")

    # Securely stored hashed password (not plaintext)
    password_hash: Mapped[str] = mapped_column(String(255))

    # Soft-disable users without deleting their rows
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
