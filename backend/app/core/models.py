from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class PageIndex(Base):
    """
    The core index for crawled pages.
    Replaces the old `index` table in PHP.
    """
    __tablename__ = "page_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, unique=True, nullable=False, index=True)
    url_hash = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(Text)
    content = Column(Text)  # Raw cleaned content
    
    # Vector storage for RAG (Retrieval Augmented Generation)
    # This assumes the pgvector extension is installed on the DB
    embedding = Column(Text) # Simplified as Text for initial scaffolding, will be Vector type in production
    
    metadata_json = Column(JSONB) # Stores robots.txt status, response times, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CrawlQueue(Base):
    """
    Replaces the recursive memory arrays from the PHP version.
    Allows for asynchronous, distributed crawling.
    """
    __tablename__ = "crawl_queue"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    status = Column(String, default="pending") # pending, processing, completed, failed
    attempts = Column(Integer, default=0)
    next_crawl_at = Column(DateTime(timezone=True), server_default=func.now())
