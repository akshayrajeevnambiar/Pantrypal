# app/routers/items.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.security.deps import get_current_user, require_roles, get_db
from app.models.items import Item
from app.schemas.items import ItemCreate, ItemUpdate, ItemOut, ItemListResponse

router = APIRouter(prefix="/items", tags=["Items"])

# ----- helpers ---------------------------------------------------------------

def _ensure_unique_name(db: Session, name: str, exclude_id: Optional[int] = None) -> None:
    """
    Enforce case-insensitive uniqueness for item.name.
    If exclude_id is provided, ignore that row (for updates).
    """
    q = db.query(Item).filter(func.lower(Item.name) == func.lower(name))
    if exclude_id is not None:
        q = q.filter(Item.id != exclude_id)
    if db.query(q.exists()).scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item name already exists")

def _get_item_or_404(db: Session, item_id: int) -> Item:
    item = db.query(Item).get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

def _to_item_out(item: Item) -> ItemOut:
    """
    Canonical serializer for Item → ItemOut, including computed fields.
    """
    return ItemOut(
        id=item.id,
        name=item.name,
        base_unit=item.base_unit,
        par_level=item.par_level,
        is_active=item.is_active,
        current_qty=item.current_qty,  # requires Commit 14 model/migration
        is_below_par=(item.current_qty < item.par_level) if item.par_level is not None else None,
    )

# ----- routes ----------------------------------------------------------------

@router.post(
    "",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> ItemOut:
    """
    Create a new item. Admin/Manager only.
    - Enforces case-insensitive unique name
    - Validates base_unit & par_level (handled by Pydantic)
    """
    _ensure_unique_name(db, payload.name)

    item = Item(
        name=payload.name.strip(),
        base_unit=payload.base_unit,
        par_level=payload.par_level or 0,
        is_active=True,
        # current_qty is defaulted at DB level; setting explicitly is fine too:
        # current_qty=0,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_item_out(item)

@router.get("", response_model=ItemListResponse)
def list_items(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # any authenticated user
    q: Optional[str] = Query(None, description="Search by name (case-insensitive substring)"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ItemListResponse:
    """
    List items with optional search, active filter, and pagination.
    """
    query = db.query(Item)

    if q:
        query = query.filter(func.lower(Item.name).like(f"%{q.lower()}%"))
    if active is not None:
        query = query.filter(Item.is_active == active)

    total = query.count()
    rows = query.order_by(func.lower(Item.name)).limit(limit).offset(offset).all()

    return ItemListResponse(
        items=[_to_item_out(i) for i in rows],
        total=total,
        limit=limit,
        offset=offset,
    )

@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
) -> ItemOut:
    """
    Get a single item by id. Any authenticated user.
    """
    item = _get_item_or_404(db, item_id)
    return _to_item_out(item)

@router.put(
    "/{item_id}",
    response_model=ItemOut,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
) -> ItemOut:
    """
    Update an item. Admin/Manager only.
    - Optional fields; only provided ones are applied.
    - Name uniqueness is enforced when name changes.
    """
    item = _get_item_or_404(db, item_id)

    if payload.name is not None:
        new_name = payload.name.strip()
        if new_name != item.name:
            _ensure_unique_name(db, new_name, exclude_id=item.id)
        item.name = new_name

    if payload.base_unit is not None:
        item.base_unit = payload.base_unit

    if payload.par_level is not None:
        item.par_level = payload.par_level

    if payload.is_active is not None:
        item.is_active = payload.is_active

    db.commit()
    db.refresh(item)
    return _to_item_out(item)

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
def soft_delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    """
    Soft-delete an item by setting is_active=False. Idempotent.
    Admin/Manager only.
    """
    item = _get_item_or_404(db, item_id)
    if item.is_active:
        item.is_active = False
        db.commit()
    # 204 No Content (nothing to return)

@router.post(
    "/{item_id}/restore",
    response_model=ItemOut,
    dependencies=[Depends(require_roles("admin", "manager"))],
)
def restore_item(item_id: int, db: Session = Depends(get_db)) -> ItemOut:
    """
    Restore a soft-deleted item by setting is_active=True.
    Admin/Manager only.
    """
    item = _get_item_or_404(db, item_id)
    if not item.is_active:
        item.is_active = True
        db.commit()
        db.refresh(item)
    return _to_item_out(item)

# HARD DELETE (admin only): permanently remove an item if it has no history.
try:
    from app.models.counts import Count  # noqa: F401
    HAS_COUNTS = True
except Exception:
    HAS_COUNTS = False

@router.delete(
    "/{item_id}/hard",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles("admin"))],  # ADMIN ONLY
)
def hard_delete_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """
    Permanently delete an item **only if** it has no dependent history.
    - Admin only.
    - If the `counts` table exists and any row references this item -> 409 Conflict.
    - Otherwise, the row is removed from the DB (no soft-delete).
    """
    item = _get_item_or_404(db, item_id)

    if HAS_COUNTS:
        exists = db.query(Count).filter(Count.item_id == item.id).first() is not None
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot hard-delete: item has historical counts. Use soft delete instead.",
            )

    db.delete(item)
    db.commit()
    # 204 No Content
