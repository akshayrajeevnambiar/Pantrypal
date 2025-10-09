# app/routers/counts.py
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.orm import SessionLocal
from app.models.counts import Count
from app.models.items import Item
from app.models.users import User
from app.security.deps import get_current_user, require_roles
from app.schemas.counts import CountSubmit, CountOut, PendingListResponse

router = APIRouter(prefix="/counts", tags=["Counts"])

# --- shared deps ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _ensure_item_active(db: Session, item_id: int) -> Item:
    item = db.query(Item).get(item_id)
    if not item or not item.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found or inactive")
    return item

def _count_to_out(row: Count) -> CountOut:
    return CountOut(
        id=row.id,
        item_id=row.item_id,
        item_name=row.item.name if row.item else "",
        count=row.count,
        status=row.status,  # type: ignore
        submitted_by_id=row.submitted_by,
        submitted_by_name=row.submitter.name if row.submitter else "",
        submitted_at=row.submitted_at,
        approved_by_id=row.approved_by,
        approved_by_name=row.approver.name if row.approver else None,
        approved_at=row.approved_at,
    )

# --- routes ---

@router.post("/submit", response_model=CountOut, status_code=status.HTTP_201_CREATED)
def submit_count(
    payload: CountSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CountOut:
    """
    Any authenticated user can submit a count (typical: counter).
    Creates a pending count row.
    """
    item = _ensure_item_active(db, payload.item_id)

    c = Count(
        item_id=item.id,
        count=payload.count,
        status="pending",
        submitted_by=current_user.id,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return _count_to_out(c)

@router.get("/pending", response_model=PendingListResponse, dependencies=[Depends(require_roles("admin","manager"))])
def list_pending_counts(
    db: Session = Depends(get_db),
    item_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PendingListResponse:
    """
    Manager/Admin: review queue of pending counts (with pagination and optional filter by item).
    """
    q = db.query(Count).filter(Count.status == "pending")
    if item_id is not None:
        q = q.filter(Count.item_id == item_id)

    total = q.count()
    rows = (
        q.order_by(Count.submitted_at.desc())
         .limit(limit)
         .offset(offset)
         .all()
    )
    return PendingListResponse(items=[_count_to_out(r) for r in rows], total=total, limit=limit, offset=offset)

@router.post("/{count_id}/approve", response_model=CountOut, dependencies=[Depends(require_roles("admin","manager"))])
def approve_count(
    count_id: int,
    db: Session = Depends(get_db),
    reviewer: User = Depends(get_current_user),
) -> CountOut:
    """
    Manager/Admin: approve a pending count.
    """
    row = db.query(Count).get(count_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Count not found")
    if row.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending counts can be approved")

    # Ensure the item still exists & is active
    _ensure_item_active(db, row.item_id)

    row.status = "approved"
    row.approved_by = reviewer.id
    row.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return _count_to_out(row)

@router.post("/{count_id}/reject", response_model=CountOut, dependencies=[Depends(require_roles("admin","manager"))])
def reject_count(
    count_id: int,
    db: Session = Depends(get_db),
    reviewer: User = Depends(get_current_user),
) -> CountOut:
    """
    Manager/Admin: reject a pending count.
    """
    row = db.query(Count).get(count_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Count not found")
    if row.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending counts can be rejected")

    # Still record who reviewed the rejection
    row.status = "rejected"
    row.approved_by = reviewer.id
    row.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return _count_to_out(row)
