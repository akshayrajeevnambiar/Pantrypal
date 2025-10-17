# app/routers/counts.py
from typing import Optional, List, Union
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.security.deps import get_current_user, require_roles, get_db
from app.models.counts import Count
from app.models.items import Item
from app.models.users import User
from app.schemas.counts import CountSubmit, CountOut, PendingListResponse, CountBatchSubmit


router = APIRouter(prefix="/counts", tags=["Counts"])


def _item_active_or_404(db: Session, item_id: int) -> Item:
    item = db.query(Item).get(item_id)
    if not item or not item.is_active:
        raise HTTPException(status_code=404, detail="Item not found or inactive")
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
        notes=row.notes,
        approved_by_id=row.approved_by,
        approved_by_name=row.approver.name if row.approver else None,
        approved_at=row.approved_at,
    )


@router.post(
    "/submit",
    response_model=Union[CountOut, List[CountOut]],
    status_code=status.HTTP_201_CREATED,
)
def submit_count(
    payload: Union[CountSubmit, CountBatchSubmit],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accept either a single CountSubmit or a CountBatchSubmit (list of counts).
    Creates one or many 'pending' count rows.
    """
    payload_list = payload.counts if isinstance(payload, CountBatchSubmit) else [payload]

    results: List[CountOut] = []
    for entry in payload_list:
        item = db.query(Item).get(entry.item_id)
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail=f"Item {entry.item_id} not found or inactive")

        row = Count(
            item_id=item.id,
            count=entry.count,
            status="pending",
            submitted_by=current_user.id,
            submitted_at=datetime.now(timezone.utc),
            notes=entry.notes,
        )
        db.add(row)
        db.flush()  # assign ID
        db.refresh(row)
        results.append(_count_to_out(row))

    db.commit()
    return results[0] if len(results) == 1 else results


@router.get(
    "/pending",
    response_model=PendingListResponse,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
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
    return PendingListResponse(
        items=[_count_to_out(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("", response_model=PendingListResponse)
def list_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    item_id: Optional[int] = Query(None),
    mine: bool = Query(False, description="If true, return only my submissions"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PendingListResponse:
    """
    List counts with optional filters.
    - Any authenticated user can view.
    - 'mine=true' restricts to own submissions.
    """
    q = db.query(Count)

    if status_filter:
        q = q.filter(Count.status == status_filter)
    if item_id:
        q = q.filter(Count.item_id == item_id)
    if mine:
        q = q.filter(Count.submitted_by == current_user.id)

    total = q.count()
    rows = q.order_by(Count.submitted_at.desc()).limit(limit).offset(offset).all()
    return PendingListResponse(
        items=[_count_to_out(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{count_id}/approve",
    response_model=CountOut,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
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
        raise HTTPException(status_code=404, detail="Count not found")
    if row.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending counts can be approved")

    # Ensure the item is still active
    _item_active_or_404(db, row.item_id)

    row.status = "approved"
    row.approved_by = reviewer.id
    row.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return _count_to_out(row)


@router.post(
    "/{count_id}/reject",
    response_model=CountOut,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
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
        raise HTTPException(status_code=404, detail="Count not found")
    if row.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending counts can be rejected")

    row.status = "rejected"
    row.approved_by = reviewer.id
    row.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return _count_to_out(row)
