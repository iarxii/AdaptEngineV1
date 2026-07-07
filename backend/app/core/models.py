from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    projects = relationship("ProjectProfile", back_populates="owner")

class ProjectProfile(Base):
    __tablename__ = "project_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    root_url = Column(String, nullable=False)
    max_depth = Column(Integer, default=3)
    settings = Column(JSONB, default={}) # Store rate limits, exclusions, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="projects")
    pages = relationship("PageIndex", back_populates="project")
    queue = relationship("CrawlQueue", back_populates="project")
    logs = relationship("CrawlLog", back_populates="project")

class PageIndex(Base):
    __tablename__ = "page_index"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_profiles.id"), nullable=False, index=True)
    url = Column(String, nullable=False)
    url_hash = Column(String, index=True) # For fast deduplication
    title = Column(String)
    content = Column(Text)
    metadata_json = Column(JSONB)
    embedding = Column(Text) # Will be converted to Vector type if pgvector is active
    last_indexed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    project = relationship("ProjectProfile", back_populates="pages")

class CrawlQueue(Base):
    __tablename__ = "crawl_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_profiles.id"), nullable=False, index=True)
    url = Column(String, nullable=False)
    status = Column(String, default="pending", index=True) # pending, processing, completed, failed
    priority = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    next_crawl_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("ProjectProfile", back_populates="queue")

class CrawlLog(Base):
    __tablename__ = "crawl_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("project_profiles.id"), nullable=False, index=True)
    queue_id = Column(UUID(as_uuid=True), ForeignKey("crawl_queue.id"), nullable=True)
    url = Column(String, nullable=False)
    http_status = Column(Integer)
    latency_ms = Column(Float)
    error_message = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("ProjectProfile", back_populates="logs")
