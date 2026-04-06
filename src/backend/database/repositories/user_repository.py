"""
User Repository - Data access layer for User models.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models import User
from .base import BaseRepository

class UserRepository(BaseRepository):
    """Repository for User entities."""

    def _get_model_class(self):
        return User

    def _to_dict(self, entity: Any) -> Dict[str, Any]:
        return {
            'id': entity.id,
            'email': entity.email,
            'name': entity.name,
            'age': entity.age,
            'gender': entity.gender,
            'height': entity.height,
            'weight_current': entity.weight_current,
            'activity_level': entity.activity_level,
            'goal': entity.goal,
            'profile_data': entity.profile_data or {},
        }

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def create_user(self, email: str, name: str, age: int, gender: str,
                   height: float, weight_current: float, activity_level: str,
                   goal: str, profile_data: Any = None) -> User:
        user = User(
            email=email, name=name, age=age, gender=gender,
            height=height, weight_current=weight_current,
            activity_level=activity_level, goal=goal,
            profile_data=profile_data or {}
        )
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def update_weight(self, user_id: int, new_weight: float):
        return self.update(user_id, weight_current=new_weight)
