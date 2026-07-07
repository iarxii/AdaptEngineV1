import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWT, jwt
from passlib.context import CryptContext

from models import Base, User, ProjectProfile, CrawlQueue, PageIndex, CrawlLog

# --- CONFIGURATION & DATABASE SETUP ---
# In production, these would be loaded from a .env file via pydantic-settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://adapt_admin:change_me_securely@localhost:5432/adaptengine_v1")
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_jwt_key_here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create tables (In a real scenario, we use Alembic migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdaptEngine V1 API")

# --- SCHEMAS (Pydantic) ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    class Config:
        from_attributes = True

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

class Token(BaseModel):
    access_token: str
    token_type: str

# --- DEPENDENCIES ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTH ENDPOINTS ---
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_in.email,
        password_hash=pwd_context.hash(user_in.password),
        api_key=str(uuid.uuid4()) # Simple API key generation
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- PROJECT ENDPOINTS ---
@app.post("/projects/", response_model=ProjectOut)
async def create_project(project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_project = ProjectProfile(
        user_id=current_user.id,
        name=project_in.name,
        base_url=project_in.base_url,
        config=project_in.config
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.get("/projects/", response_model=List[ProjectOut])
async def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ProjectProfile).filter(ProjectProfile.user_id == current_user.id).all()

# --- QUEUE ENDPOINTS ---
@app.post("/projects/{project_id}/queue/")
async def add_to_queue(project_id: str, urls: List[str], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify project ownership
    project = db.query(ProjectProfile).filter(ProjectProfile.id == project_id, ProjectProfile.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    for url in urls:
        # Avoid duplicates within the same project
        exists = db.query(CrawlQueue).filter(CrawlQueue.project_id == project_id, CrawlQueue.url == url).first()
        if not exists:
            queue_item = CrawlQueue(project_id=project_id, url=url)
            db.add(queue_item)
    
    db.commit()
    return {"status": "success", "added": len(urls)}
