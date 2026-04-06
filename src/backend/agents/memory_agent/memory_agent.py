"""
Memory Agent - Tracks patterns:
- favorite meals
- recurring foods
- hunger patterns
- Meal timing preferences

Enables personalization over time.
"""
from typing import Dict, Any, Optional, List
from datetime import date, datetime, timedelta
from .base_agent import BaseAgent
from ...database.models import MemoryPattern
from ...database import get_db


class MemoryAgent(BaseAgent):
    """
    Stores and retrieves user memory patterns to enable personalization.
    """

    def __init__(self, agent_id: str = "memory", db_session=None):
        super().__init__(agent_id=agent_id, name="Memory Agent")
        self.db = db_session
        self.patterns: Dict[int, Dict[str, Any]] = {}  # in-memory cache user_id -> patterns

    async def initialize(self) -> None:
        await super().initialize()
        if not self.db:
            self.db = next(get_db())

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action")
        if not action:
            raise ValueError("Action is required")

        user_id = request["user_id"]

        actions = {
            "get_patterns": self._action_get_patterns,
            "update_patterns": self._action_update_patterns,
            "get_favorite_ingredients": self._action_get_favorite_ingredients,
            "get_meal_suggestions": self._action_get_meal_suggestions,
            "record_meal": self._action_record_meal,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](request)

    async def _action_get_patterns(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        patterns = await self.get_patterns(user_id)
        return {"user_id": user_id, "patterns": patterns}

    async def _action_update_patterns(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        meal_data = request.get("meal_data", {})
        date_str = request.get("date", date.today().isoformat())
        await self.update_patterns(user_id, date_str, meal_data)
        return {"success": True, "user_id": user_id}

    async def _action_get_favorite_ingredients(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        ingredients = await self.get_favorite_ingredients(user_id)
        return {"user_id": user_id, "favorite_ingredients": ingredients}

    async def _action_get_meal_suggestions(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        meal_type = request.get("meal_type", "lunch")
        suggestions = await self.get_meal_suggestions_based_on_memory(user_id, meal_type)
        return {"user_id": user_id, "meal_type": meal_type, "suggestions": suggestions}

    async def _action_record_meal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        meal_data = request["meal_data"]
        await self.record_meal(user_id, meal_data)
        return {"success": True}

    # --- Public API methods ---

    async def get_patterns(self, user_id: int) -> Dict[str, Any]:
        """Get stored patterns for user."""
        if user_id in self.patterns:
            return self.patterns[user_id]
        # In real implementation, load from memory_patterns table
        default = {
            "favorite_meals": [],
            "recurring_foods": ["banana", "oatmeal", "eggs", "chicken breast"],
            "hunger_patterns": {
                "afternoon_slump": False,
                "late_night": False,
                "mid_morning_crash": False,
            },
            "meal_timing_preferences": {
                "breakfast_early": True,
                "late_dinner": False,
                "snacks_between_meals": True
            },
            "preferred_equipment": ["stove", "oven"],
            "last_updated": datetime.utcnow().isoformat()
        }
        self.patterns[user_id] = default
        return default

    async def update_patterns(self, user_id: int, meal_date: str, meal_data: Dict[str, Any]) -> None:
        """Update patterns based on recent meal."""
        # In a real implementation, would analyze and update DB
        patterns = await self.get_patterns(user_id)
        food_items = meal_data.get("food_items", [])
        # Simple update: extract food names and add to recurring if seen multiple times
        for item in food_items:
            name = item.get("name", "").lower()
            if name and name not in patterns["recurring_foods"]:
                patterns["recurring_foods"].append(name)
        patterns["last_updated"] = datetime.utcnow().isoformat()
        self.patterns[user_id] = patterns

    async def get_favorite_ingredients(self, user_id: int) -> List[str]:
        """Get list of user's long-term favorite ingredients."""
        patterns = await self.get_patterns(user_id)
        return patterns.get("recurring_foods", [])

    async def get_meal_suggestions_based_on_memory(
        self,
        user_id: int,
        meal_type: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Suggest meals that align with user's memory patterns."""
        patterns = await self.get_patterns(user_id)

        suggestions = []
        for food in patterns.get("favorite_meals", [])[:limit]:
            suggestions.append({
                "type": "memory_based",
                "name": food,
                "reason": "Past favorite based on your history",
                "meal_type": meal_type
            })

        return suggestions

    async def record_meal(self, user_id: int, meal_data: Dict[str, Any]) -> None:
        """Record a meal for later pattern recognition."""
        await self.update_patterns(user_id, date.today().isoformat(), meal_data)
