# app/schemas/counts.py
from datetime import datetime
from typing import Literal, Optional, List

from pydantic import BaseModel, Field

Status = Literal["pending", "approved", "rejected"]


class CountSubmit(BaseModel):
    item_id: int
    count: int = Field(ge=0)
    notes: Optional[str] = None


class CountOut(BaseModel):
    id: int
    item_id: int
    item_name: str
    count: int
    status: Status
    submitted_by_id: int
    submitted_by_name: str
    submitted_at: datetime
    notes: Optional[str] = None
    approved_by_id: Optional[int] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_count: Optional[int] = None


class PendingListResponse(BaseModel):
    items: List[CountOut]
    total: int
    limit: int
    offset: int


class CountBatchSubmit(BaseModel):
    counts: List[CountSubmit]
