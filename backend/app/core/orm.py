# backend/app/core/orm.py
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.db import engine

class Base(DeclarativeBase):
    """
    Declarative Base that all ORM models will subclass.
    SQLAlchemy uses this to collect table metadata.
    """
    pass

# Session factory you'll use later inside request handlers/services.
# Note: we aren't using it yet; it's here for completeness.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)