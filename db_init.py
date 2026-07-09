import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base

# Load environment variables from .env file
load_dotenv()

# Database credentials from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db") # Default to docker service name
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "adaptengine")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initializes the database schema. 
    Note: In a production environment, use Alembic for migrations.
    """
    print(f"Connecting to database at {DB_HOST}...")
    try:
        # Enable pgvector extension first so that Vector columns can be created
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()

        # Create tables
        Base.metadata.create_all(bind=engine)
            
        print("✅ Database schema initialized and pgvector extension enabled.")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise e

if __name__ == "__main__":
    init_db()
