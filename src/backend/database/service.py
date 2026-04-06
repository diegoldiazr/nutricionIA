"""
Database Service - Manages database connections and provides session handling.

Provides:
- Engine and session management
- Database initialization
- Session context manager
"""
from contextlib import contextmanager
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from core.exceptions import DatabaseError
import logging

from .models import Base

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database connection manager."""

    def __init__(self, database_url: str):
        """
        Initialize service with database URL.

        Args:
            database_url: SQLAlchemy connection URL
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize()

    def _initialize(self) -> None:
        """Create SQLAlchemy engine and session factory."""
        url = self.database_url
        if url.startswith('sqlite'):
            self.engine = create_engine(
                url,
                connect_args={'check_same_thread': False},
                echo=False
            )
        else:
            self.engine = create_engine(
                url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    async def init_db(self) -> None:
        """Create all tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created")
        except SQLAlchemyError as e:
            logger.error(f"Database init failed: {e}")
            raise DatabaseError(f"Failed to create tables: {e}")

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions.

        Usage:
            with db.get_session() as session:
                user = session.query(User).get(1)
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def health(self) -> dict:
        """Check database health."""
        try:
            with self.get_session() as session:
                from sqlalchemy import text
                result = session.execute(text("SELECT 1"))
                result.fetchone()
            return {"status": "healthy", "url": self.database_url}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def close(self) -> None:
        """Dispose all connections."""
        if self.engine:
            self.engine.dispose()
