# backend/app/models/items.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean
from app.core.orm import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Friendly, unique name for the ingredient
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    # Base unit for stock counts and PAR math: "g" | "ml" | "pcs"
    base_unit: Mapped[str] = mapped_column(String(10))

    # Minimum desired level in base units
    par_level: Mapped[int] = mapped_column(Integer, default=0)

    # Hide without deleting (keeps history intact)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # NEW: live on-hand quantity (in base_unit)
    current_qty: Mapped[int] = mapped_column(Integer, nullable=False, default=0)