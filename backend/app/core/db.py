import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://pantrypal:pantrypal@localhost:5432/pantrypal")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)