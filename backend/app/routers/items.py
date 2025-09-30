# app/routers/items.py
from fastapi import APIRouter, Depends
from app.security.deps import require_roles

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("")
def create_item_guard_only(current_user = Depends(require_roles("admin", "manager"))):
    """
    Placeholder route to demonstrate role enforcement.
    Only 'admin' and 'manager' can access this.
    """
    return {"ok": True, "message": f"user {current_user.email} is allowed to create items"}
