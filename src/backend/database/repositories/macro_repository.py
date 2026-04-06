"""
Macro Repository - Data access layer for DailyMacro models.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date
from ..models import DailyMacro
from .base import BaseRepository

class MacroRepository(BaseRepository):
    """Repository for DailyMacro entities."""

    def _get_model_class(self):
        return DailyMacro

    def _to_dict(self, entity: Any) -> Dict[str, Any]:
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'date': entity.date.isoformat() if isinstance(entity.date, date) else str(entity.date),
            'calories': entity.calories,
            'carbs': entity.carbs,
            'protein': entity.protein,
            'fat': entity.fat,
            'meals': entity.meals or [],
        }

    def get_by_user_and_date(self, user_id: int, target_date: date) -> Optional[DailyMacro]:
        return self.session.query(DailyMacro).filter(
            DailyMacro.user_id == user_id,
            DailyMacro.date == target_date
        ).first()

    def upsert_for_date(self, user_id: int, target_date: date, **kwargs) -> DailyMacro:
        existing = self.get_by_user_and_date(user_id, target_date)
        if existing:
            for key, value in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            self.session.flush()
            self.session.refresh(existing)
            return existing
        entity = DailyMacro(user_id=user_id, date=target_date, **kwargs)
        self.session.flush()
        return entity
