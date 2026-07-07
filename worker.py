import time
import uuid
import logging
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from models import Base, CrawlQueue, ProjectProfile, CrawlLog, PageIndex

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CrawlerWorker")

class CrawlerWorker:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def run_once(self):
        """
        A single iteration of the worker: 
        1. Find a pending task.
        2. Fetch project config.
        3. Execute request.
        4. Log result and update queue.
        """
        db = self.SessionLocal()
        try:
            # 1. Find the highest priority pending task
            task = db.query(CrawlQueue).filter(CrawlQueue.status == 'pending').order_by(CrawlQueue.priority.desc()).first()
            
            if not task:
                logger.info("No pending tasks in queue.")
                return False

            # Mark as processing immediately to avoid duplicate workers picking it up
            task.status = 'processing'
            db.commit()

            # 2. Fetch associated Project Profile for config
            project = db.query(ProjectProfile).filter(ProjectProfile.id == task.project_id).first()
            if not project:
                logger.error(f"Project {task.project_id} not found for task {task.id}")
                task.status = 'failed'
                db.commit()
                return True

            # Apply rate limiting from config
            rate_limit = project.config.get('rate_limit', 1.0)
            time.sleep(rate_limit)

            logger.info(f"Crawling {task.url} for project {project.name}")
            
            # 3. Execute Request
            start_time = datetime.utcnow()
            try:
                with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                    response = client.get(task.url)
                    latency = (datetime.utcnow() - start_time).total_seconds()
                    
                    # Record success in logs
                    self._log_result(db, task, project, response.status_code, latency)
                    
                    # Update queue status
                    task.status = 'done'
                    
                    # 4. Index the content (Simplified for Phase 4)
                    # In Phase 5, we will integrate the Embedding pipeline here
                    self._index_page(db, task, project, response.text)

            except Exception as e:
                latency = (datetime.utcnow() - start_time).total_seconds()
                logger.error(f"Error crawling {task.url}: {str(e)}")
                self._log_result(db, task, project, 0, latency, error_msg=str(e))
                task.status = 'failed'

            db.commit()
            return True

        except Exception as e:
            logger.critical(f"Worker system failure: {str(e)}")
            return False
        finally:
            db.close()

    def _log_result(self, db: Session, task: CrawlQueue, project: ProjectProfile, status_code: int, latency: float, error_msg: str = None):
        log_entry = CrawlLog(
            project_id=project.id,
            queue_id=task.id,
            status_code=status_code,
            latency=latency,
            error_log=error_msg,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)

    def _index_page(self, db: Session, task: CrawlQueue, project: ProjectProfile, content: str):
        """
        Basic indexing logic. 
        Vector embeddings are handled in Phase 5.
        """
        # Check if page already exists in index
        page = db.query(PageIndex).filter(PageIndex.url == task.url).first()
        if not page:
            page = PageIndex(url=task.url, project_id=project.id)
            db.add(page)
        
        page.content = content
        page.last_indexed = datetime.utcnow()
        # page.embedding = ... (Phase 5)

if __name__ == "__main__":
    # This block allows running the worker as a standalone script for testing
    import os
    DB_URL = os.getenv("DATABASE_URL", "postgresql://adapt_admin:change_me_securely@localhost:5432/adaptengine_v1")
    worker = CrawlerWorker(DB_URL)
    
    logger.info("Starting Crawler Worker Loop...")
    while True:
        did_work = worker.run_once()
        if not did_work:
            time.sleep(10) # Sleep if no tasks were found
