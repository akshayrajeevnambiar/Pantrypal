from fastapi import FastAPI
from sqlalchemy import text
from app.core.db import engine
from app.routers import auth as auth_router
from app.routers import items as items_router

app = FastAPI(title="Pantrypal API", version="0.1.0")

@app.get("/", tags=["Root"], include_in_schema=False)
def root():
    return {"app": "Pantrypal API", "docs": "/docs", "health": "/health"}

@app.get("/health", tags=["Health"])
def read_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    return {"ok": True, "db": db_status}

app.include_router(auth_router.router)
app.include_router(items_router.router)