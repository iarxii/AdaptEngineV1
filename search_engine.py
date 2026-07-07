import os
import numpy as np
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

# Import existing infrastructure
from main import app, get_db, get_current_user
from models import PageIndex, ProjectProfile

# We use 'sentence-transformers' for local embeddings or 'openai' for cloud.
# For this implementation, we'll provide a pluggable interface.
try:
    from sentence_transformers import SentenceTransformer
    # Local model: all-MiniLM-L6-v2 (384 dims) or similar. 
    # For the 1536 dim defined in models.py, we typically use OpenAI.
    # Here we implement a mock/local bridge that can be swapped.
    model = SentenceTransformer('all-MiniLM-L6-v2') 
    EMBEDDING_DIM = 384 
except ImportError:
    model = None
    EMBEDDING_DIM = 1536 # Default to the model defined in ERD

# --- SCHEMAS ---
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    url: str
    content: str
    score: float

# --- EMBEDDING ENGINE ---
def get_embedding(text: str):
    """
    Generates a vector embedding for the given text.
    """
    if model:
        # Local SentenceTransformers implementation
        embedding = model.encode(text)
        return embedding.tolist()
    else:
        # This is where the OpenAI API call would go in production:
        # response = openai.Embedding.create(input=text, model="text-embedding-3-small")
        # return response['data'][0]['embedding']
        
        # Fallback for demonstration: Random vector of correct dimension
        return np.random.rand(EMBEDDING_DIM).tolist()

# --- VECTOR SEARCH ENDPOINTS ---

@app.post("/projects/{project_id}/search", response_model=List[SearchResult])
async def semantic_search(
    project_id: str, 
    search_req: SearchQuery, 
    current_user: any = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Performs a vector similarity search (Cosine Distance) on the indexed pages of a project.
    """
    # 1. Verify project ownership
    project = db.query(ProjectProfile).filter(
        ProjectProfile.id == project_id, 
        ProjectProfile.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")

    # 2. Embed the user query
    query_vector = get_embedding(search_req.query)

    # 3. Perform pgvector distance query (<-> is Euclidean, <=> is Cosine)
    # Note: SQLAlchemy supports raw SQL for pgvector operators
    results = db.query(PageIndex).filter(
        PageIndex.project_id == project_id
    ).order_by(
        PageIndex.embedding.cosine_distance(query_vector)
    ).limit(search_req.top_k).all()

    # 4. Format results
    output = []
    for res in results:
        # Calculate similarity score (1 - distance)
        dist = res.embedding.cosine_distance(query_vector) if hasattr(res, 'cosine_distance') else 0
        output.append(SearchResult(
            url=res.url,
            content=res.content[:500] + "...", # Snippet
            score=1.0 - float(dist) if dist else 0.0
        ))

    return output

@app.post("/projects/{project_id}/reindex")
async def reindex_project(
    project_id: str, 
    current_user: any = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Trigger a batch re-embedding of all content for a specific project.
    """
    project = db.query(ProjectProfile).filter(
        ProjectProfile.id == project_id, 
        ProjectProfile.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    pages = db.query(PageIndex).filter(PageIndex.project_id == project_id).all()
    count = 0
    
    for page in pages:
        if page.content:
            page.embedding = get_embedding(page.content)
            count += 1
    
    db.commit()
    return {"status": "success", "pages_indexed": count}
