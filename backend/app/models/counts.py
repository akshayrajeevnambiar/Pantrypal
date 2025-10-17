# app/models/counts.py
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Enum, Index  # <-- add Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.orm import Base

# NEW: canonical enum definition in the model (mirrors your Pydantic Literal)
StatusEnum = Enum("pending", "approved", "rejected", name="count_status")

class Count(Base):
    __tablename__ = "counts"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    # CHANGED: use DB enum + default
    status: Mapped[str] = mapped_column(StatusEnum, nullable=False, server_default="pending")

    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    notes: Mapped[Optional[str]] = mapped_column(Text)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    item = relationship("Item", backref="count_rows")
    submitter = relationship("User", foreign_keys=[submitted_by], backref="submitted_counts")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_counts")

    # NEW: helpful indexes for common filters
    __table_args__ = (
        Index("ix_counts_status", "status"),
        Index("ix_counts_item_id", "item_id"),
        Index("ix_counts_submitted_by", "submitted_by"),
    )
