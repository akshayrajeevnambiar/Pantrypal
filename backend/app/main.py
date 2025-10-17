# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.db import engine
from app.routers import auth as auth_router
from app.routers import items as items_router
from app.routers import counts as counts_router
from app.routers import dashboard as dashboard_router  # if you added commit 15
import os

app = FastAPI(title="Pantrypal API", version="0.1.0")

# CORS — allow your frontend (adjust or load from env)
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Routers
app.include_router(auth_router.router)
app.include_router(items_router.router)
app.include_router(counts_router.router)
app.include_router(dashboard_router.router)
