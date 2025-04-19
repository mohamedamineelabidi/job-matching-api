from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

from models.database import Base

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://job_posts:j1o2b3_p4o5s6t7s8@linkedin-job-posts.postgres.database.azure.com:5432/postgres?sslmode=require"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()