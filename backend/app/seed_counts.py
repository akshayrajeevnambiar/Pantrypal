# app/seed_counts.py
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.orm import SessionLocal
from app.models.users import User
from app.models.items import Item
from app.models.counts import Count

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(func.lower(User.email) == func.lower(email)).first()

def get_item(db: Session, name: str) -> Item | None:
    return db.query(Item).filter(func.lower(Item.name) == func.lower(name)).first()

def run():
    db: Session = SessionLocal()
    try:
        counter = get_user_by_email(db, "counter@pantrypal.dev")
        manager = get_user_by_email(db, "manager@pantrypal.dev")
        if not (counter and manager):
            print("⚠️ Missing seed users. Run: python -m app.seed_users")
            return

        tomatoes = get_item(db, "Tomatoes")
        rice     = get_item(db, "Basmati Rice 10kg")
        oil      = get_item(db, "Cooking Oil")

        if not all([tomatoes, rice, oil]):
            print("⚠️ Missing items. Run: python -m app.seed_items")
            return

        now = datetime.now(timezone.utc)

        # Create a few historical counts:
        demo_counts = [
            # pending
            Count(item_id=oil.id, count=1400, status="pending",
                  submitted_by=counter.id, submitted_at=now - timedelta(hours=2), notes="closing shift"),
            # approved (snapshot + inventory sync is done by router in real flow, but we set here for demo)
            Count(item_id=tomatoes.id, count=10, status="approved", approved_count=10,
                  submitted_by=counter.id, approved_by=manager.id,
                  submitted_at=now - timedelta(days=1, hours=3), approved_at=now - timedelta(days=1, hours=2),
                  notes="prep"),
            # rejected
            Count(item_id=rice.id, count=2500, status="rejected",
                  submitted_by=counter.id, submitted_at=now - timedelta(days=2), notes="inaccurate"),
        ]

        for c in demo_counts:
            db.add(c)

        db.commit()
        print("✅ Seeded counts (pending/approved/rejected).")
    finally:
        db.close()

if __name__ == "__main__":
    run()
