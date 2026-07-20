import asyncio
import logging
import uuid
import numpy as np
import httpx
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.core.models import CrawlQueue, ProjectProfile, CrawlLog, PageIndex

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CrawlerWorker")

# --- EMBEDDING ENGINE ---
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    EMBEDDING_DIM = 384 
except ImportError:
    model = None
    EMBEDDING_DIM = 1536 

def get_embedding_sync(text: str):
    """Synchronous wrapper for the embedding model."""
    if model:
        return model.encode(text).tolist()
    return np.random.rand(EMBEDDING_DIM).tolist()

async def get_embedding(text: str):
    """
    Asynchronous wrapper for embedding generation.
    Offloads the CPU-intensive encoding to a separate thread to avoid blocking the event loop.
    """
    return await asyncio.to_thread(get_embedding_sync, text)

class CrawlerWorker:
    def __init__(self):
        self.is_running = False
        self.client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the persistent HTTP client."""
        if self.client is None or self.client.is_closed:
            logger.info("Initializing persistent HTTP client session...")
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                follow_redirects=True,
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
            )
        return self.client

    async def run_forever(self):
        """Main loop for the crawler worker."""
        self.is_running = True
        logger.info("Crawler Worker started. Looking for tasks...")
        
        try:
            while self.is_running:
                did_work = await self.process_next_task()
                if not did_work:
                    await asyncio.sleep(10) # Idle wait
        finally:
            await self.close()

    async def close(self):
        """Clean up resources."""
        if self.client:
            await self.client.aclose()
            logger.info("HTTP client session closed.")

    async def process_next_task(self) -> bool:
        """
        Processes a single task from the queue.
        """
        async with async_session() as db:
            try:
                # 1. Find highest priority pending task
                query = select(CrawlQueue).where(CrawlQueue.status == 'pending').order_by(CrawlQueue.priority.desc()).limit(1)
                result = await db.execute(query)
                task = result.scalar_one_or_none()

                if not task:
                    return False

                # Mark as processing
                task.status = 'processing'
                await db.commit()

                # 2. Fetch project config
                proj_query = select(ProjectProfile).where(ProjectProfile.id == task.project_id)
                proj_result = await db.execute(proj_query)
                project = proj_result.scalar_one_or_none()

                if not project:
                    task.status = 'failed'
                    await db.commit()
                    return True

                # Rate limiting
                rate_limit = project.config.get('rate_limit', 1.0)
                await asyncio.sleep(rate_limit)

                logger.info(f"Crawling {task.url} for project {project.name}")
                
                # 3. Use Persistent Client
                client = await self._get_client()
                start_time = datetime.utcnow()
                try:
                    response = await client.get(task.url)
                    latency = (datetime.utcnow() - start_time).total_seconds()
                    
                    await self._log_result(db, task, project, response.status_code, latency)
                    task.status = 'done'
                    
                    # 4. Index and Vectorize (Now non-blocking)
                    await self._index_page(db, task, project, response.text)

                except Exception as e:
                    latency = (datetime.utcnow() - start_time).total_seconds()
                    logger.error(f"Error crawling {task.url}: {str(e)}")
                    await self._log_result(db, task, project, 0, latency, error_msg=str(e))
                    task.status = 'failed'

                await db.commit()
                return True

            except Exception as e:
                logger.critical(f"Worker system failure: {str(e)}")
                return False

    async def _log_result(self, db: AsyncSession, task: CrawlQueue, project: ProjectProfile, status_code: int, latency: float, error_msg: str = None):
        log_entry = CrawlLog(
            project_id=project.id,
            queue_id=task.id,
            status_code=status_code,
            latency=latency,
            error_log=error_msg,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)

    async def _index_page(self, db: AsyncSession, task: CrawlQueue, project: ProjectProfile, content: str):
        """
        Indexes page content and generates embeddings for semantic search.
        """
        query = select(PageIndex).where(PageIndex.url == task.url)
        result = await db.execute(query)
        page = result.scalar_one_or_none()

        if not page:
            page = PageIndex(url=task.url, project_id=project.id)
            db.add(page)
        
        page.content = content
        page.last_indexed = datetime.utcnow()
        
        # --- THE LOOP CLOSURE ---
        # Now using the async wrapper to avoid blocking the main loop
        page.embedding = await get_embedding(content)
        
        logger.info(f"Successfully indexed and vectorized {task.url}")

if __name__ == "__main__":
    async def main():
        worker = CrawlerWorker()
        try:
            await worker.run_forever()
        except KeyboardInterrupt:
            await worker.close()
    
    asyncio.run(main())
