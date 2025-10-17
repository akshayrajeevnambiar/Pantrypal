from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.security.deps import get_current_user, require_roles, get_db
from app.models.items import Item
from app.models.counts import Count
from app.models.users import User
from app.schemas.counts import CountOut
from app.schemas.items import ItemOut
from app.routers.items import _to_item_out   # reuse serializer

router = APIRouter(prefix="/dash", tags=["Dashboard"])


@router.get("/pending-approvals",
            response_model=List[CountOut],
            dependencies=[Depends(require_roles("admin", "manager"))])
def pending_approvals(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Manager/Admin: view all pending counts needing approval."""
    rows = (
        db.query(Count)
        .filter(Count.status == "pending")
        .order_by(Count.submitted_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return [
        CountOut(
            id=r.id,
            item_id=r.item_id,
            item_name=r.item.name if r.item else "",
            count=r.count,
            status=r.status,
            submitted_by_id=r.submitted_by,
            submitted_by_name=r.submitter.name if r.submitter else "",
            submitted_at=r.submitted_at,
            notes=r.notes,
            approved_by_id=r.approved_by,
            approved_by_name=r.approver.name if r.approver else None,
            approved_at=r.approved_at,
            approved_count=r.approved_count,
        )
        for r in rows
    ]


@router.get("/low-stock", response_model=List[ItemOut])
def low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Show all active items currently below par level."""
    rows = (
        db.query(Item)
        .filter(Item.is_active == True, Item.current_qty < Item.par_level)
        .order_by(Item.name)
        .all()
    )
    return [_to_item_out(i) for i in rows]


@router.get("/my-submissions", response_model=List[CountOut])
def my_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
):
    """Show counts submitted by the current user, optionally filtered by status."""
    q = db.query(Count).filter(Count.submitted_by == current_user.id)
    if status_filter:
        q = q.filter(Count.status == status_filter)
    rows = q.order_by(Count.submitted_at.desc()).all()

    return [
        CountOut(
            id=r.id,
            item_id=r.item_id,
            item_name=r.item.name if r.item else "",
            count=r.count,
            status=r.status,
            submitted_by_id=r.submitted_by,
            submitted_by_name=r.submitter.name if r.submitter else "",
            submitted_at=r.submitted_at,
            notes=r.notes,
            approved_by_id=r.approved_by,
            approved_by_name=r.approver.name if r.approver else None,
            approved_at=r.approved_at,
            approved_count=r.approved_count,
        )
        for r in rows
    ]
