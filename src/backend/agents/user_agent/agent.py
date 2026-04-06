"""
User Agent - Manages user data including profile, preferences, weight history, and meal logging.

Uses repository pattern for data access.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from ..base_agent import BaseAgent
from core.events import EventType
from core.exceptions import AgentError


class UserAgent(BaseAgent):
    """
    Manages all user-related data operations.
    """

    def __init__(
        self,
        agent_id: str = "user",
        repositories: Dict[str, Any] = None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="User Agent", event_bus=event_bus)
        self.repos = repositories or {}
        self.user_repo = repositories.get('users') if repositories else None
        self.macro_repo = repositories.get('macros') if repositories else None
        self.pref_repo = repositories.get('preferences') if repositories else None

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action")
        if not action:
            raise AgentError("Action is required")

        handlers = {
            "create_profile": self._handle_create_profile,
            "get_profile": self._handle_get_profile,
            "update_profile": self._handle_update_profile,
            "get_preferences": self._handle_get_preferences,
            "update_preferences": self._handle_update_preferences,
            "log_weight": self._handle_log_weight,
            "get_weight_history": self._handle_get_weight_history,
            "log_meal": self._handle_log_meal,
            "get_daily_macros": self._handle_get_daily_macros,
        }

        if action not in handlers:
            raise AgentError(f"Unknown action: {action}")

        return await handlers[action](request)

    async def _handle_create_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if not self.user_repo:
            raise AgentError("User repository not available")

        user = self.user_repo.create_user(
            email=request["email"],
            name=request["name"],
            age=request["age"],
            gender=request["gender"],
            height=request["height"],
            weight_current=request["weight_current"],
            activity_level=request["activity_level"],
            goal=request["goal"],
            profile_data=request.get("profile_data", {})
        )

        if self.pref_repo:
            self.pref_repo.create_for_user(user.id)

        if self.event_bus:
            self._publish_event(EventType.USER_CREATED, {
                'user_id': user.id,
                'email': user.email
            })

        return self.user_repo._to_dict(user)

    async def _handle_get_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise AgentError(f"User {user_id} not found")
        return self.user_repo._to_dict(user)

    async def _handle_get_preferences(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        pref = self.pref_repo.get_by_user_id(user_id)
        if not pref:
            return {}
        return self.pref_repo._to_dict(pref)

    async def _handle_log_meal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        meal_data = request.get("meal_data", {})

        meal_date = meal_data.get("date", date.today())
        if isinstance(meal_date, str):
            meal_date = date.fromisoformat(meal_date)

        macros = meal_data.get("macros", {})
        calories = macros.get("calories", 0)
        protein = macros.get("protein", 0)
        carbs = macros.get("carbs", 0)
        fat = macros.get("fat", 0)

        existing = self.macro_repo.get_by_user_and_date(user_id, meal_date)
        if existing:
            existing.calories += calories
            existing.protein += protein
            existing.carbs += carbs
            existing.fat += fat
            if not existing.meals:
                existing.meals = []
            existing.meals.append(meal_data)
            self.macro_repo.session.flush()
            self.macro_repo.session.refresh(existing)
            macro_entry = existing
        else:
            macro_entry = self.macro_repo.upsert_for_date(
                user_id=user_id,
                target_date=meal_date,
                calories=calories,
                protein=protein,
                carbs=carbs,
                fat=fat,
                meals=[meal_data]
            )

        if self.event_bus:
            self.event_bus.publish(EventType.MEAL_LOGGED, {
                'user_id': user_id,
                'date': meal_date.isoformat(),
                'calories': calories
            })

        return self.macro_repo._to_dict(macro_entry)

    async def _handle_get_daily_macros(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        target_date = request.get("date", date.today())
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)

        macro = self.macro_repo.get_by_user_and_date(user_id, target_date)
        if not macro:
            return {
                "user_id": user_id,
                "date": target_date.isoformat(),
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
                "meals": []
            }

        return self.macro_repo._to_dict(macro)

    # Stub methods for later implementation
    async def _handle_update_profile(self, request: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Update profile not yet implemented")
    async def _handle_get_weight_history(self, request: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Weight history not yet implemented")
    async def _handle_log_weight(self, request: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Log weight not yet implemented")
    async def _handle_update_preferences(self, request: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Update preferences not yet implemented")
