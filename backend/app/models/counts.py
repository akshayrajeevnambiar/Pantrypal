# app/models/count.py
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.orm import Base


class Count(Base):
    __tablename__ = "counts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Which item is being counted
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)

    # Quantity submitted (in the item's base_unit)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Workflow status: "pending" | "approved" | "rejected"
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # Who submitted the count (counter) + when
    submitted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Optional notes from the submitter
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Who approved/rejected + when (nullable until decision)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    item = relationship("Item", backref="count_rows")
    submitter = relationship("User", foreign_keys=[submitted_by], backref="submitted_counts")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_counts")

    # NEW: store what value was approved at that moment
    approved_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
