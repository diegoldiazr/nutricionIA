"""
Memory Agent - Tracks patterns for personalization.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from core.events import EventType
from core.exceptions import AgentError


class MemoryAgent(BaseAgent):
    """
    Tracks patterns:
    - Favorite meals
    - Recurring foods
    - Hunger patterns
    """

    def __init__(
        self,
        agent_id: str = "memory",
        repositories=None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Memory Agent", event_bus=event_bus)
        self.repos = repositories or {}
        self.memory_repo = repositories.get('memory') if repositories else None

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "get_patterns")

        if action == "record_meal":
            return await self.record_meal(request)
        elif action == "get_patterns":
            return await self.get_patterns(request)
        elif action == "update_patterns":
            return await self.update_patterns(request)
        else:
            raise AgentError(f"Unknown action: {action}")

    async def record_meal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a meal to memory patterns.
        Updates favorite meals, recurring foods.
        """
        user_id = request["user_id"]
        meal_data = request.get("meal_data", {})

        if not self.memory_repo:
            return {"status": "skipped", "reason": "Memory repository not available"}

        # Get existing memory or create new
        memory = self.memory_repo.get_by_user_id(user_id)

        if memory:
            meals = memory.favorite_meals or []
            foods = memory.recurring_foods or []
        else:
            meals, foods = [], []

        # Update meals
        meal_name = meal_data.get("name", "Unknown Meal")
        if meal_name not in [m.get("name", "") for m in meals]:
            meals.append({"name": meal_name, "count": 1})
        else:
            for m in meals:
                if m["name"] == meal_name:
                    m["count"] = m.get("count", 0) + 1

        # Update recurring foods
        ingredients = meal_data.get("ingredients", [])
        for ingredient in ingredients:
            if ingredient.lower() not in [f.lower() for f in foods]:
                foods.append(ingredient)

        # Save
        if not memory:
            self.memory_repo.upsert(
                user_id=user_id,
                favorite_meals=meals,
                recurring_foods=foods
            )
        else:
            self.memory_repo.update_for_user(
                user_id=user_id,
                favorite_meals=meals,
                recurring_foods=foods
            )

        return {
            "status": "recorded",
            "meal_name": meal_name,
            "total_meals_logged": len(meals)
        }

    async def get_patterns(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory patterns for user."""
        user_id = request["user_id"]
        if not self.memory_repo:
            return {}

        memory = self.memory_repo.get_by_user_id(user_id)
        if not memory:
            return {}

        return self.memory_repo._to_dict(memory)

    async def update_patterns(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update memory patterns for user."""
        user_id = request["user_id"]
        updates = {k: v for k, v in request.items() if k not in ('action', 'user_id')}

        if not self.memory_repo:
            raise AgentError("Memory repository not available")

        memory = self.memory_repo.get_by_user_id(user_id)
        if memory:
            self.memory_repo.upsert(user_id, **updates)
            return {"status": "updated"}
        else:
            self.memory_repo.upsert(
                user_id=user_id,
                favorite_meals=request.get("favorite_meals", []),
                recurring_foods=request.get("recurring_foods", []),
                hunger_patterns=request.get("hunger_patterns", {}),
                meal_timing_preferences=request.get("meal_timing_preferences", {})
            )
            return {"status": "created"}

    # Stub method for repository update
    async def _update_memory(self, request: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Not yet implemented")
