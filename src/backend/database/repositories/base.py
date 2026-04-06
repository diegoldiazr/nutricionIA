"""
Base Repository - Abstract base class for all repositories.

Provides common CRUD operations with SQLAlchemy.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """
    Generic base repository for SQLAlchemy models.
    
    All repositories should inherit from this and implement:
    - _get_model_class() - return the SQLAlchemy model class
    - _to_dict(entity) - convert entity to dict
    """
    
    def __init__(self, session: Session):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session instance
        """
        self.session = session
        self._model_class = self._get_model_class()
    
    @abstractmethod
    def _get_model_class(self) -> type:
        """Return the SQLAlchemy model class for this repository."""
        pass
    
    @abstractmethod
    def _to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        pass
    
    def create(self, entity: T) -> T:
        """
        Create a new entity.
        
        Args:
            entity: Entity instance to create
            
        Returns:
            Created entity with ID populated
        """
        try:
            self.session.add(entity)
            self.session.flush()
            self.session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.session.rollback()
            raise
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by primary key.
        
        Args:
            entity_id: Primary key value
            
        Returns:
            Entity or None if not found
        """
        return self.session.query(self._model_class).get(entity_id)
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Any = None
    ) -> List[T]:
        """
        Get all entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            order_by: Optional ordering column
            
        Returns:
            List of entities
        """
        query = self.session.query(self._model_class)
        if order_by is not None:
            query = query.order_by(order_by)
        return query.offset(skip).limit(limit).all()
    
    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """
        Update entity by ID.
        
        Args:
            entity_id: Primary key
            **kwargs: Fields to update
            
        Returns:
            Updated entity or None if not found
        """
        entity = self.get_by_id(entity_id)
        if entity:
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            try:
                self.session.flush()
                self.session.refresh(entity)
                return entity
            except SQLAlchemyError:
                self.session.rollback()
                raise
        return None
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Primary key
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.get_by_id(entity_id)
        if entity:
            self.session.delete(entity)
            try:
                self.session.flush()
                return True
            except SQLAlchemyError:
                self.session.rollback()
                raise
        return False
    
    def count(self) -> int:
        """Get total count of entities."""
        return self.session.query(self._model_class).count()
    
    def exists(self, entity_id: int) -> bool:
        """Check if entity with given ID exists."""
        return self.get_by_id(entity_id) is not None
