"""
Seed initial users into the database for PantryPal MVP.
- admin: full access
- manager: mid-level access
- counter: read/update counts only
"""

from sqlalchemy.orm import Session
from app.core.orm import SessionLocal, Base
from app.models.users import User
from app.security.passwords import hash_password

def seed_users():
    # Start a session
    db: Session = SessionLocal()

    # Define seed data (plaintext passwords only here, they’ll be hashed)
    seed_data = [
        {"email": "admin@pantrypal.dev", "name": "Admin User", "role": "admin", "password": "admin123"},
        {"email": "manager@pantrypal.dev", "name": "Manager User", "role": "manager", "password": "manager123"},
        {"email": "counter@pantrypal.dev", "name": "Counter User", "role": "counter", "password": "counter123"},
    ]

    for user in seed_data:
        # Check if user already exists (avoid duplicates if re-run)
        existing = db.query(User).filter(User.email == user["email"]).first()
        if existing:
            print(f"User {user['email']} already exists, skipping.")
            continue

        # Create new User with hashed password
        new_user = User(
            email=user["email"],
            name=user["name"],
            role=user["role"],
            password_hash=hash_password(user["password"]),
            is_active=True,
        )
        db.add(new_user)

    db.commit()
    db.close()
    print("✅ Seed users inserted.")

if __name__ == "__main__":
    seed_users()
