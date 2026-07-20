from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.core.database import async_session
from app.core.models import ProjectProfile, CrawlQueue
from app.api.auth import get_current_user, User

router = APIRouter(prefix="/projects", tags=["Projects"])

# --- SCHEMAS ---
class ProjectCreate(BaseModel):
    name: str
    base_url: str
    config: Optional[dict] = {}

class ProjectOut(BaseModel):
    id: str
    name: str
    base_url: str
    config: dict
    class Config:
        from_attributes = True

# --- ENDPOINTS ---
@router.post("/", response_model=ProjectOut)
async def create_project(project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(async_session)):
    new_project = ProjectProfile(
        user_id=current_user.id,
        name=project_in.name,
        base_url=project_in.base_url,
        config=project_in.config
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[ProjectOut])
async def list_projects(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(async_session)):
    result = await db.execute(select(ProjectProfile).filter(ProjectProfile.user_id == current_user.id))
    return result.scalars().all()

@router.post("/{project_id}/queue/")
async def add_to_queue(project_id: str, urls: List[str], current_user: User = Depends(get_current_user), db: AsyncSession = Depends(async_session)):
    # Verify project ownership
    result = await db.execute(select(ProjectProfile).filter(ProjectProfile.id == project_id, ProjectProfile.user_id == current_user.id))
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    for url in urls:
        # Avoid duplicates within the same project
        q_result = await db.execute(select(CrawlQueue).filter(CrawlQueue.project_id == project_id, CrawlQueue.url == url))
        if not q_result.scalars().first():
            queue_item = CrawlQueue(project_id=project_id, url=url)
            db.add(queue_item)
    
    await db.commit()
    return {"status": "success", "added": len(urls)}
