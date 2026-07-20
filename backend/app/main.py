from fastapi import FastAPI
from app.core.database import init_db, async_session
from app.api.search import router as search_router
from app.api.auth import router as auth_router
from app.api.projects import router as project_router
from app.core.crawler import CrawlerWorker
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AdaptEngineV1")

app = FastAPI(
    title="AdaptEngineV1 API",
    description="Knowledge Acquisition Module for AI_Codex",
    version="1.0.0"
)

# Register Routers
app.include_router(search_router)
app.include_router(auth_router)
app.include_router(project_router)

# Global worker instance
crawler_worker = CrawlerWorker()

@app.on_event("startup")
async def startup_event():
    # 1. Initialize Database (Migrations/Extensions)
    await init_db()
    logger.info("Database initialized successfully.")
    
    # 2. Start the crawler as a background task
    # Using create_task ensures the worker runs concurrently with the API
    asyncio.create_task(crawler_worker.run_forever())
    logger.info("Crawler Worker background task initiated.")

@app.on_event("shutdown")
async def shutdown_event():
    crawler_worker.is_running = False
    logger.info("Shutting down AdaptEngineV1...")

@app.get("/")
async def root():
    return {
        "status": "online", 
        "module": "AdaptEngineV1", 
        "integration": "AI_Codex",
        "features": ["Semantic Search", "Async Crawling", "Automatic Vectorization"]
    }
