from fastapi import FastAPI
from app.core.database import init_db

app = FastAPI(
    title="AdaptEngineV1 API",
    description="Knowledge Acquisition Module for AI_Codex",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"status": "online", "module": "AdaptEngineV1", "integration": "AI_Codex"}
