from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.models import PageIndex

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/")
async def search_pages(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Search the page index for the query string.
    Note: Currently implements basic SQL ILIKE search. 
    Planned: Integration with pgvector for semantic search.
    """
    # Search across title, description, and content
    query = select(PageIndex).where(
        (PageIndex.title.ilike(f"%{q}%")) | 
        (PageIndex.description.ilike(f"%{q}%")) | 
        (PageIndex.content.ilike(f"%{q}%"))
    ).limit(limit).offset(offset)

    result = await db.execute(query)
    pages = result.scalars().all()

    return {
        "query": q,
        "results": [
            {
                "id": str(p.id),
                "url": p.url,
                "title": p.title,
                "description": p.description,
                "created_at": p.created_at
            } for p in pages
        ],
        "count": len(pages)
    }

@router.get("/stats")
async def get_index_stats(db: AsyncSession = Depends(get_db)):
    """Returns total number of indexed pages."""
    query = select(func.count()).select_from(PageIndex)
    result = await db.execute(query)
    count = result.scalar()
    return {"total_indexed_pages": count}
