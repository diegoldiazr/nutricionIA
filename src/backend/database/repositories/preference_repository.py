"""
Preference Repository - Data access layer for Preference models.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models import Preference
from .base import BaseRepository

class PreferenceRepository(BaseRepository):
    """Repository for Preference entities."""

    def _get_model_class(self):
        return Preference

    def _to_dict(self, entity: Any) -> Dict[str, Any]:
        return {
            'id': entity.id,
            'user_id': entity.user_id,
            'dietary_restrictions': entity.dietary_restrictions or [],
            'allergies': entity.allergies or [],
            'favorite_foods': entity.favorite_foods or [],
            'disliked_foods': entity.disliked_foods or [],
            'cooking_equipment': entity.cooking_equipment or [],
            'prep_time_max': entity.prep_time_max,
            'difficulty_max': entity.difficulty_max,
            'meals_per_day': entity.meals_per_day,
            'snack_preference': entity.snack_preference,
        }

    def get_by_user_id(self, user_id: int) -> Optional[Preference]:
        return self.session.query(Preference).filter(Preference.user_id == user_id).first()

    def create_for_user(self, user_id: int, **kwargs) -> Preference:
        pref = Preference(user_id=user_id, **kwargs)
        self.session.add(pref)
        self.session.flush()
        self.session.refresh(pref)
        return pref
