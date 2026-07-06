from fastapi import FastAPI
from app.core.database import init_db
from app.api.search import router as search_router
from app.core.crawler import CrawlerWorker
from app.core.database import SessionLocal
import asyncio

app = FastAPI(
    title="AdaptEngineV1 API",
    description="Knowledge Acquisition Module for AI_Codex",
    version="1.0.0"
)

app.include_router(search_router)

@app.on_event("startup")
async def startup_event():
    await init_db()
    
    # Start the crawler in the background
    async def run_crawler():
        async with SessionLocal() as db:
            worker = CrawlerWorker(db)
            await worker.run()

    asyncio.create_task(run_crawler())

@app.get("/")
async def root():
    return {"status": "online", "module": "AdaptEngineV1", "integration": "AI_Codex"}
