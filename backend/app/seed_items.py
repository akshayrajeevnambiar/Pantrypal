# app/seed_items.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.orm import SessionLocal
from app.models.items import Item

DEMO_ITEMS = [
    {"name": "Tomatoes",        "base_unit": "pcs", "par_level": 15, "current_qty": 8},
    {"name": "Chicken Thighs",  "base_unit": "pcs", "par_level": 20, "current_qty": 12},
    {"name": "Basmati Rice 10kg","base_unit": "g",  "par_level": 5000, "current_qty": 3000},
    {"name": "Cooking Oil",     "base_unit": "ml",  "par_level": 5000, "current_qty": 1200},
    {"name": "Onions",          "base_unit": "pcs", "par_level": 20, "current_qty": 18},
]

def upsert_item(db: Session, data: dict):
    existing = (
        db.query(Item)
        .filter(func.lower(Item.name) == func.lower(data["name"]))
        .first()
    )
    if existing:
        # update only fields we control in seed
        existing.base_unit = data["base_unit"]
        existing.par_level = data["par_level"]
        existing.current_qty = data["current_qty"]
        existing.is_active = True
        return existing

    new_item = Item(
        name=data["name"],
        base_unit=data["base_unit"],
        par_level=data["par_level"],
        current_qty=data["current_qty"],
        is_active=True,
    )
    db.add(new_item)
    return new_item

def run():
    db: Session = SessionLocal()
    try:
        for row in DEMO_ITEMS:
            upsert_item(db, row)
        db.commit()
        print("✅ Seeded items.")
    finally:
        db.close()

if __name__ == "__main__":
    run()
