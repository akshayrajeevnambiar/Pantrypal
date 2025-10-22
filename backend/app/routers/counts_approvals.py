# app/routers/counts_approvals.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.users import User
from app.models.counts import Count, CountStatus  # enum: pending/approved/rejected
from app.models.items import Item
from app.security.deps import get_current_user, require_roles

router = APIRouter(prefix="/counts", tags=["counts"])

@router.get("/pending")
def list_pending(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(["manager","admin"]))
):
    q = db.query(Count).filter(Count.status == CountStatus.pending).order_by(Count.created_at.desc())
    total = q.count()
    items = [c.to_out() for c in q.limit(limit).offset(offset).all()]
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/{count_id}/approve")
def approve_count(
    count_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    reviewer: User = Depends(require_roles(["manager","admin"]))
):
    c = db.query(Count).filter(Count.id == count_id).first()
    if not c: raise HTTPException(404, "Count not found")
    if c.status != CountStatus.pending: raise HTTPException(409, "Count not pending")
    item = db.query(Item).filter(Item.id == c.item_id).first()
    if not item: raise HTTPException(404, "Item not found or inactive")

    c.status = CountStatus.approved
    c.approved_by_id = reviewer.id
    c.approved_count = c.count
    item.current_qty = c.count
    db.add_all([c, item]); db.commit(); db.refresh(c)
    return c.to_out()

@router.post("/{count_id}/reject")
def reject_count(
    count_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    reviewer: User = Depends(require_roles(["manager","admin"]))
):
    c = db.query(Count).filter(Count.id == count_id).first()
    if not c: raise HTTPException(404, "Count not found")
    if c.status != CountStatus.pending: raise HTTPException(409, "Count not pending")

    c.status = CountStatus.rejected
    c.approved_by_id = reviewer.id
    db.add(c); db.commit(); db.refresh(c)
    return c.to_out()
