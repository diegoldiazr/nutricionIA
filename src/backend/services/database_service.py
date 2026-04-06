"""
Database Service - Wraps SQLAlchemy operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from .config.settings import settings

Base = declarative_base()

class DatabaseService:
    """SQLAlchemy-based database service."""
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or settings.DATABASE_URL
        self.engine = create_engine(
            self.db_url,
            connect_args={"check_same_thread": False} if "sqlite" in self.db_url else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    async def init_db(self):
        """Create all tables."""
        from ..database.models import Base
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    async def close(self):
        """Close database connection."""
        self.engine.dispose()
