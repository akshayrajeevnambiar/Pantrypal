# app/routers/counts.py
from typing import List, Union
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.security.deps import get_current_user, require_roles, get_db
from app.models.counts import Count
from app.models.items import Item
from app.models.users import User
from app.schemas.counts import CountSubmit, CountOut, CountBatchSubmit

router = APIRouter(prefix="/counts", tags=["Counts"])

@router.post(
    "/submit",
    response_model=Union[CountOut, List[CountOut]],
    status_code=status.HTTP_201_CREATED,
)
def submit_count(
    payload: Union[CountSubmit, CountBatchSubmit],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # or Depends(require_roles("counter")) if you prefer
):
    # Normalize payload to a list
    payload_list: List[CountSubmit] = (
        payload.counts if isinstance(payload, CountBatchSubmit) else [payload]  # type: ignore[attr-defined]
    )

    results: List[CountOut] = []

    for entry in payload_list:
        # 1) Block another pending for the same item (until approved/rejected)
        existing_pending = (
            db.query(Count)
            .filter(Count.item_id == entry.item_id, Count.status == "pending")
            .first()
        )
        if existing_pending:
            raise HTTPException(
                status_code=409,
                detail=f"Pending count already exists for item_id={entry.item_id}. Please approve/reject it first.",
            )

        # 2) Validate item exists and is active
        item = db.query(Item).get(entry.item_id)
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail=f"Item {entry.item_id} not found or inactive")

        # 3) Create the pending count
        row = Count(
            item_id=item.id,
            count=entry.count,
            status="pending",
            submitted_by=current_user.id,
            submitted_at=datetime.now(timezone.utc),
            notes=entry.notes,
        )
        db.add(row)
        db.flush()
        db.refresh(row)

        results.append(CountOut(
            id=row.id,
            item_id=row.item_id,
            item_name=item.name,
            count=row.count,
            status=row.status,  # type: ignore
            submitted_by_id=row.submitted_by,
            submitted_by_name=current_user.name,
            submitted_at=row.submitted_at,
            notes=row.notes,
            approved_by_id=row.approved_by,
            approved_by_name=row.approver.name if row.approver else None,
            approved_at=row.approved_at,
            approved_count=row.approved_count,
        ))

    db.commit()
    return results[0] if len(results) == 1 else results
