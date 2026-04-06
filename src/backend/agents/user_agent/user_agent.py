"""
User Agent - Manages user data: profile, preferences, weight history, meal logs.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from .base_agent import BaseAgent
from ...database.models import User,WeightHistory, DailyMacro, Preference
from ...database import get_db


class UserAgent(BaseAgent):
    """
    Manages all user-specific data:
    - Profile (age, gender, height, weight, goals)
    - Preferences (dietary restrictions, equipment)
    - Weight history
    - Meal logging
    """

    def __init__(self, agent_id: str = "user", db_session=None):
        super().__init__(agent_id=agent_id, name="User Agent")
        self.db = db_session

    async def initialize(self) -> None:
        await super().initialize()
        # Initialize DB connection if not provided
        if not self.db:
            self.db = next(get_db())

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route user-related requests to appropriate methods.

        Request types:
        - get_profile: {"action": "get_profile", "user_id": int}
        - create_profile: {"action": "create_profile", "user_data": Dict}
        - update_profile: {"action": "update_profile", "user_id": int, "updates": Dict}
        - get_preferences: {"action": "get_preferences", "user_id": int}
        - set_preferences: {"action": "set_preferences", "user_id": int, "preferences": Dict}
        - log_meal: {"action": "log_meal", "user_id": int, "meal_data": Dict}
        - get_daily_macros: {"action": "get_daily_macros", "user_id": int, "date": str}
        - log_weight: {"action": "log_weight", "user_id": int, "weight": float, "date": str}
        - get_weight_history: {"action": "get_weight_history", "user_id": int, "days": int}
        """
        action = request.get("action")
        if not action:
            raise ValueError("Action is required")

        handlers = {
            "get_profile": self._handle_get_profile,
            "create_profile": self._handle_create_profile,
            "update_profile": self._handle_update_profile,
            "get_preferences": self._handle_get_preferences,
            "set_preferences": self._handle_set_preferences,
            "log_meal": self._handle_log_meal,
            "get_daily_macros": self._handle_get_daily_macros,
            "log_weight": self._handle_log_weight,
            "get_weight_history": self._handle_get_weight_history,
        }

        if action not in handlers:
            raise ValueError(f"Unknown action: {action}")

        return await handlers[action](request)

    async def _handle_get_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        # In real implementation, query DB
        return {
            "id": user_id,
            "name": "Demo User",
            "email": f"user{user_id}@example.com",
            "age": 30,
            "gender": "male",
            "height": 175.0,
            "weight_current": 80.0,
            "activity_level": "moderate",
            "goal": "lose_weight",
            "created_at": datetime.utcnow().isoformat()
        }

    async def _handle_create_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_data = request["user_data"]
        # Would create in database
        return {
            "id": 1,
            **user_data,
            "created_at": datetime.utcnow().isoformat()
        }

    async def _handle_update_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        updates = request["updates"]
        # Would update in database
        return {"success": True, "user_id": user_id, "updated_fields": list(updates.keys())}

    async def _handle_get_preferences(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        # Would query preferences table
        return {
            "user_id": user_id,
            "dietary_restrictions": [],
            "favorite_foods": ["chicken breast", "brown rice", "broccoli"],
            "disliked_foods": ["shellfish", "olives"],
            "cooking_equipment": ["airfryer", "stove", "oven"],
            "prep_time_max": 45,
            "difficulty_max": "medium"
        }

    async def _handle_set_preferences(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        preferences = request["preferences"]
        # Would save to database
        return {"success": True, "user_id": user_id}

    async def _handle_log_meal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        meal_data = request["meal_data"]
        # Would create meal record in database
        return {
            "id": 1,
            "user_id": user_id,
            "date": meal_data.get("date", date.today().isoformat()),
            "meal_type": meal_data.get("meal_type", "lunch"),
            "food_items": meal_data.get("food_items", []),
            "notes": meal_data.get("notes"),
            "created_at": datetime.utcnow().isoformat()
        }

    async def _handle_get_daily_macros(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        target_date = request["date"]
        # Would query database and sum food items
        return {
            "date": target_date,
            "calories": 1200,
            "protein": 90,
            "carbs": 150,
            "fat": 40
        }

    async def _handle_log_weight(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        weight = request["weight"]
        log_date = request.get("date", date.today().isoformat())
        # Would insert into weight_history
        return {"success": True, "user_id": user_id, "weight": weight, "date": log_date}

    async def _handle_get_weight_history(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        days = request.get("days", 30)
        # Would query weight_history table
        return {
            "user_id": user_id,
            "entries": [
                {"date": (date.today()).isoformat(), "weight": 80.0 - i*0.2}
                for i in range(min(days, 7))
            ]
        }
