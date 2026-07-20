from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import numpy as np

from app.core.database import get_db
from app.core.models import PageIndex, ProjectProfile

router = APIRouter(prefix="/search", tags=["Search"])

# --- EMBEDDING ENGINE ---
# In a production environment, this would be a separate service or a cached class.
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    EMBEDDING_DIM = 384 
except ImportError:
    model = None
    EMBEDDING_DIM = 1536 

def get_embedding(text_content: str):
    """
    Generates a vector embedding for the given text.
    """
    if model:
        return model.encode(text_content).tolist()
    else:
        # Fallback for demonstration/dev
        return np.random.rand(EMBEDDING_DIM).tolist()

# --- ENDPOINTS ---

@router.post("/semantic")
async def semantic_search(
    project_id: str, 
    q: str = Query(..., description="Semantic search query"),
    top_k: int = Query(5, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Performs a vector similarity search (Cosine Distance) on indexed pages.
    """
    # 1. Verify project exists
    project_query = await db.execute(select(ProjectProfile).where(ProjectProfile.id == project_id))
    project = project_query.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Generate embedding for the query
    query_vector = get_embedding(q)

    # 3. Perform pgvector cosine distance search
    # We use the <=> operator for cosine distance in pgvector
    # distance = (1 - cosine_similarity)
    stmt = (
        select(PageIndex)
        .where(PageIndex.project_id == project_id)
        .order_by(PageIndex.embedding.cosine_distance(query_vector))
        .limit(top_k)
    )
    
    result = await db.execute(stmt)
    pages = result.scalars().all()

    return {
        "query": q,
        "results": [
            {
                "url": p.url,
                "content": p.content[:500] + "..." if p.content else "",
                "score": 1.0 - float(p.embedding.cosine_distance(query_vector)) if p.embedding else 0.0
            } for p in pages
        ]
    }

@router.get("/")
async def keyword_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Fallback keyword search using ILIKE.
    """
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
    query = select(func.count()).select_from(PageIndex)
    result = await db.execute(query)
    count = result.scalar()
    return {"total_indexed_pages": count}
