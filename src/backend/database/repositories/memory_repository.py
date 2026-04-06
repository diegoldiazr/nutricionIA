"""
Memory Repository - Data access layer for MemoryPattern models.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models import MemoryPattern
from .base import BaseRepository

class MemoryRepository(BaseRepository):
    """Repository for MemoryPattern entities."""

    def _get_model_class(self):
        return MemoryPattern

    def _to_dict(self, entity: Any) -> Dict[str, Any]:
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'favorite_meals': entity.favorite_meals or [],
            'recurring_foods': entity.recurring_foods or [],
            'hunger_patterns': entity.hunger_patterns or {},
            'meal_timing_preferences': entity.meal_timing_preferences or {},
            'adherence_score': entity.adherence_score,
            'favorite_cuisines': entity.favorite_cuisines or [],
            'avoided_ingredients': entity.avoided_ingredients or [],
        }

    def get_by_user_id(self, user_id: int) -> Optional[MemoryPattern]:
        return self.session.query(MemoryPattern).filter(MemoryPattern.user_id == user_id).first()

    def upsert(self, user_id: int, **kwargs) -> MemoryPattern:
        memory = self.get_by_user_id(user_id)
        if memory:
            for key, value in kwargs.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)
            self.session.flush()
            self.session.refresh(memory)
            return memory
        memory = MemoryPattern(user_id=user_id, **kwargs)
        self.session.add(memory)
        self.session.flush()
        return memory
