from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    """
    Core user account for multi-tenant access.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    projects = relationship("ProjectProfile", back_populates="owner")

class ProjectProfile(Base):
    """
    Configuration and scope for a specific crawling target.
    Allows users to maintain separate indices for different goals.
    """
    __tablename__ = "project_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    root_url = Column(String, nullable=False)
    max_depth = Column(Integer, default=3)
    
    # JSONB for flexible settings like: {"excluded_domains": ["ads.com"], "rate_limit": 2}
    settings = Column(JSONB, default={})
    status = Column(String, default="active") # active, paused, archived
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="projects")
    queue_items = relationship("CrawlQueue", back_populates="project")
    pages = relationship("PageIndex", back_populates="project")
    logs = relationship("CrawlLog", back_populates="project")

class PageIndex(Base):
    """
    The core index for crawled pages, scoped to a project.
    """
    __tablename__ = "page_index"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_profiles.id"), nullable=False, index=True)
    url = Column(String, nullable=False, index=True)
    url_hash = Column(String, index=True) # For fast deduplication checks
    title = Column(String)
    description = Column(Text)
    content = Column(Text)
    
    # Vector storage for RAG (Simplified as Text for now, replace with pgvector Vector type in prod)
    embedding = Column(Text) 
    
    metadata_json = Column(JSONB) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("ProjectProfile", back_populates="pages")

class CrawlQueue(Base):
    """
    Iterative queue for async crawling, scoped to a project.
    """
    __tablename__ = "crawl_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_profiles.id"), nullable=False, index=True)
    url = Column(String, nullable=False)
    priority = Column(Integer, default=0)
    status = Column(String, default="pending") # pending, processing, completed, failed
    attempts = Column(Integer, default=0)
    next_crawl_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("ProjectProfile", back_populates="queue_items")

class CrawlLog(Base):
    """
    Audit trail for all crawler activity.
    """
    __tablename__ = "crawl_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_profiles.id"), nullable=False, index=True)
    queue_item_id = Column(UUID(as_uuid=True), ForeignKey("crawl_queue.id"), nullable=True)
    
    level = Column(String, default="INFO") # INFO, WARN, ERROR
    message = Column(Text)
    http_status = Column(Integer)
    latency_ms = Column(Integer)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("ProjectProfile", back_populates="logs")
