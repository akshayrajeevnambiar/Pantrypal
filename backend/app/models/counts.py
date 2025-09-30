from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, DateTime
from app.core.orm import Base
from datetime import datetime

class Count(Base):
    __tablename__ = "counts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # FK to items.id
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    # Quantity in base units (g, ml, pcs)
    quantity: Mapped[int] = mapped_column(Integer)

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # FK to users.id (who made this count)
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
