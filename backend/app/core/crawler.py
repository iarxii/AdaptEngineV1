import asyncio
import logging
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from .models import PageIndex, CrawlQueue, CrawlLog, ProjectProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawler")

class CrawlerWorker:
    def __init__(self, db_session: AsyncSession, project_id: str):
        self.db = db_session
        self.project_id = project_id
        self.client = httpx.AsyncClient(
            headers={"User-Agent": "AdaptEngine/1.0 (+http://adaptengine.ai)"},
            timeout=httpx.Timeout(10.0),
            follow_redirects=True
        )

    async def get_project_config(self) -> ProjectProfile:
        result = await self.db.execute(select(ProjectProfile).where(ProjectProfile.id == self.project_id))
        return result.scalar_one()

    async def log_event(self, url: str, queue_id: str = None, status: int = None, latency: float = None, error: str = None):
        """Records the outcome of a crawl attempt into the CrawlLog."""
        stmt = insert(CrawlLog).values(
            project_id=self.project_id,
            queue_id=queue_id,
            url=url,
            http_status=status,
            latency_ms=latency,
            error_message=error,
            timestamp=datetime.utcnow()
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def fetch_next_url(self):
        """Picks the next pending URL for the specific project."""
        stmt = select(CrawlQueue).where(
            CrawlQueue.project_id == self.project_id,
            CrawlQueue.status == "pending"
        ).order_by(CrawlQueue.priority.desc(), CrawlQueue.next_crawl_at.asc()).limit(1)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def process_url(self, queue_item: CrawlQueue):
        url = queue_item.url
        start_time = datetime.utcnow()
        
        try:
            # Update status to processing
            await self.db.execute(
                update(CrawlQueue).where(CrawlQueue.id == queue_item.id).values(status="processing")
            )
            await self.db.commit()

            response = await self.client.get(url)
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log the attempt
            await self.log_event(url, queue_id=str(queue_item.id), status=response.status_code, latency=latency)

            if response.status_code == 200:
                await self.index_page(url, response.text)
                await self.discover_links(url, response.text)
                
                await self.db.execute(
                    update(CrawlQueue).where(CrawlQueue.id == queue_item.id).values(status="completed")
                )
            else:
                await self.db.execute(
                    update(CrawlQueue).where(CrawlQueue.id == queue_item.id).values(status="failed")
                )

        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self.log_event(url, queue_id=str(queue_item.id), error=str(e), latency=latency)
            await self.db.execute(
                update(CrawlQueue).where(CrawlQueue.id == queue_item.id).values(status="failed")
            )
        
        await self.db.commit()

    async def index_page(self, url: str, html_content: str):
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Clean content
        for script in soup(["script", "style"]):
            script.decompose()
            
        title = soup.title.string if soup.title else ""
        text = soup.get_text(separator=" ", strip=True)
        
        # Simple URL hash for deduplication
        url_hash = str(hash(url))

        # Upsert into PageIndex (PostgreSQL on_conflict)
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        
        stmt = pg_insert(PageIndex).values(
            project_id=self.project_id,
            url=url,
            url_hash=url_hash,
            title=title,
            content=text,
            metadata_json={"char_count": len(text)}
        ).on_conflict_do_update(
            index_elements=["url"],
            set_={"content": text, "title": title, "last_indexed_at": datetime.utcnow()}
        )
        
        await self.db.execute(stmt)

    async def discover_links(self, base_url: str, html_content: str):
        soup = BeautifulSoup(html_content, "html.parser")
        config = await self.get_project_config()
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Simple normalization and domain check
            if href.startswith("http") and config.root_url in href:
                # Avoid adding duplicates to the queue
                stmt = select(CrawlQueue).where(
                    CrawlQueue.project_id == self.project_id, 
                    CrawlQueue.url == href
                )
                result = await self.db.execute(stmt)
                if not result.scalar_one_or_none():
                    await self.db.execute(
                        insert(CrawlQueue).values(
                            project_id=self.project_id,
                            url=href,
                            status="pending"
                        )
                    )

    async def run_forever(self):
        logger.info(f"Starting Crawler Worker for project {self.project_id}")
        while True:
            item = await self.fetch_next_url()
            if item:
                await self.process_url(item)
            else:
                await asyncio.sleep(5) # Wait for new seeds
