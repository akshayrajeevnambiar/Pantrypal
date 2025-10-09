# app/schemas/items.py
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

# Allowed base units for MVP
BaseUnit = Literal["g", "ml", "pcs"]

class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    base_unit: BaseUnit
    par_level: int = Field(ge=0)

class ItemCreate(ItemBase):
    """
    Payload for creating an item.
    """
    pass

class ItemUpdate(BaseModel):
    """
    Partial update; all fields optional.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    base_unit: Optional[BaseUnit] = None
    par_level: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None

class ItemOut(BaseModel):
    id: int
    name: str
    base_unit: BaseUnit
    par_level: int
    is_active: bool

    class Config:
        from_attributes = True  # allow returning SQLAlchemy models directly

class ItemListResponse(BaseModel):
    items: List[ItemOut]
    total: int
    limit: int
    offset: int
