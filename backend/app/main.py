from fastapi import FastAPI

app = FastAPI(title="Pantrypal API", version="0.1.0")

@app.get("/health", tags=["Health"])
def read_health():
    return {"ok": True}
