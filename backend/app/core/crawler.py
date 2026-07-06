import asyncio
import logging
import hashlib
import time
from datetime import datetime
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import update, select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import PageIndex, CrawlQueue, ProjectProfile, CrawlLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawler_worker")

class CrawlerWorker:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.client = httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": "AdaptEngineV1-Crawler/1.0 (+https://iarxii.com)"},
            follow_redirects=True
        )

    async def generate_url_hash(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

    async def log_event(self, project_id: str, message: str, level: str = "INFO", 
                        queue_item_id: Optional[str] = None, status: Optional[int] = None, 
                        latency: Optional[float] = None):
        """Records crawler activity to the CrawlLog table."""
        await self.db.execute(
            insert(CrawlLog).values(
                project_id=project_id,
                queue_item_id=queue_item_id,
                level=level,
                message=message,
                http_status=status,
                latency_ms=int(latency * 1000) if latency else None
            )
        )

    async def fetch_page(self, url: str):
        start_time = time.time()
        try:
            response = await self.client.get(url)
            latency = time.time() - start_time
            response.raise_for_status()
            return response.text, response.headers, response.status_code, latency
        except Exception as e:
            latency = time.time() - start_time
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return None, None, getattr(e, 'response', 500), latency

    async def parse_content(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        title = soup.title.string if soup.title else "No Title"
        description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            description = desc_tag.get("content", "")

        text = soup.get_text(separator=' ', strip=True)
        links = [a['href'] for a in soup.find_all('a', href=True)]

        return title, description, text, links

    async def process_next_url(self, project_id: str):
        # 1. Verify Project Status
        proj_result = await self.db.execute(select(ProjectProfile).where(ProjectProfile.id == project_id))
        project = proj_result.scalar_one_or_none()
        
        if not project or project.status != "active":
            return False

        # 2. Pick a pending URL scoped to the project
        result = await self.db.execute(
            select(CrawlQueue)
            .where(CrawlQueue.project_id == project_id)
            .where(CrawlQueue.status == "pending")
            .order_by(CrawlQueue.priority.desc(), CrawlQueue.next_crawl_at.asc())
            .limit(1)
            .with_for_update()
        )
        job = result.scalar_one_or_none()

        if not job:
            return False

        logger.info(f"Project [{project.name}] Processing: {job.url}")
        
        job.status = "processing"
        await self.db.commit()

        html, headers, status_code, latency = await self.fetch_page(job.url)
        
        # Log the attempt
        await self.log_event(
            project_id=project_id, 
            message=f"Fetched {job.url}", 
            queue_item_id=str(job.id), 
            status=status_code, 
            latency=latency
        )

        if html:
            title, desc, text, links = await self.parse_content(html)
            url_hash = await self.generate_url_hash(job.url)

            # Upsert into PageIndex (now including project_id)
            await self.db.execute(
                insert(PageIndex).values(
                    project_id=project_id,
                    url=job.url,
                    url_hash=url_hash,
                    title=title,
                    description=desc,
                    content=text,
                    metadata_json={"headers": dict(headers), "status": status_code}
                ).on_conflict_do_update(
                    index_elements=[PageIndex.url], # Note: May need composite index (project_id, url) in prod
                    set_={
                        PageIndex.title: title,
                        PageIndex.description: desc,
                        PageIndex.content: text,
                        PageIndex.updated_at: datetime.utcnow()
                    }
                )
            )

            # Add discovered links to queue (scoped to project)
            for link in links:
                if link.startswith("http"):
                    # Basic check for domain consistency could be added here using project.root_url
                    await self.db.execute(
                        insert(CrawlQueue).values(
                            project_id=project_id, 
                            url=link, 
                            status="pending"
                        )
                    )

            job.status = "completed"
        else:
            job.attempts += 1
            job.status = "failed" if job.attempts >= 3 else "pending"
            await self.log_event(project_id, f"Failed to fetch {job.url} after {job.attempts} attempts", "ERROR", str(job.id))

        await self.db.commit()
        return True

    async def run_for_project(self, project_id: str):
        """Run the crawler loop for a specific project."""
        logger.info(f"Crawler Worker started for project {project_id}...")
        while True:
            processed = await self.process_next_url(project_id)
            if not processed:
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(0.1)

    async def close(self):
        await self.client.aclose()
