# app/schemas/counts.py
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field

Status = Literal["pending", "approved", "rejected"]

class CountSubmit(BaseModel):
    item_id: int
    count: int = Field(ge=0)

class CountOut(BaseModel):
    id: int
    item_id: int
    item_name: str
    count: int
    status: Status
    submitted_by_id: int
    submitted_by_name: str
    submitted_at: datetime
    approved_by_id: Optional[int] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None

class PendingListResponse(BaseModel):
    items: List[CountOut]
    total: int
    limit: int
    offset: int
