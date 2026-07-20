import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, DeclarativeBase
from pgvector.sqlalchemy import Vector

# Using DeclarativeBase for modern SQLAlchemy 2.0+ async compatibility
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("ProjectProfile", back_populates="user")

class ProjectProfile(Base):
    __tablename__ = 'project_profiles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    config = Column(JSONB, default={}) 
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    queues = relationship("CrawlQueue", back_populates="project")
    indexes = relationship("PageIndex", back_populates="project")
    logs = relationship("CrawlLog", back_populates="project")

class CrawlQueue(Base):
    __tablename__ = 'crawl_queue'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('project_profiles.id'), nullable=False)
    url = Column(String, nullable=False)
    status = Column(String, default='pending') 
    priority = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("ProjectProfile", back_populates="queues")
    logs = relationship("CrawlLog", back_populates="queue")

    __table_args__ = (UniqueConstraint('project_id', 'url', name='uq_project_url'),)

class PageIndex(Base):
    __tablename__ = 'page_index'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('project_profiles.id'), nullable=False)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    content = Column(Text)
    embedding = Column(Vector(1536)) 
    metadata_json = Column(JSONB, default={})
    last_indexed = Column(DateTime, default=datetime.utcnow)

    project = relationship("ProjectProfile", back_populates="indexes")

class CrawlLog(Base):
    __tablename__ = 'crawl_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('project_profiles.id'), nullable=False)
    queue_id = Column(UUID(as_uuid=True), ForeignKey('crawl_queue.id'), nullable=True)
    status_code = Column(Integer)
    latency = Column(Float)
    error_log = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    project = relationship("ProjectProfile", back_populates="logs")
    queue = relationship("CrawlQueue", back_populates="logs")
