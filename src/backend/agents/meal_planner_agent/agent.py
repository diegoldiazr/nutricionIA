"""
Meal Planner Agent - Generates meal suggestions using ranking logic.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from .ranking import rank_suggestions, diversify_suggestions
from core.events import EventType
from core.exceptions import AgentError


class MealPlannerAgent(BaseAgent):
    """
    Generates meal suggestions based on remaining calories, macros, and preferences.
    """

    def __init__(
        self,
        agent_id: str = "meal_planner",
        knowledge_agent=None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Meal Planner Agent", event_bus=event_bus)
        self.knowledge_agent = knowledge_agent
        self.recipe_agent = None

    @property
    def user_agent(self):
        """Get user agent via orchestrator reference (decoupled)."""
        if self._orchestrator:
            return self._orchestrator.agents.get("user")
        return None

    @user_agent.setter
    def user_agent(self, value):
        """Ignored - user_agent must be accessed via orchestrator."""
        pass

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "suggest_meals")
        if action != "suggest_meals":
            raise AgentError(f"Unknown action: {action}")

        user_id = request["user_id"]
        remaining_calories = request["remaining_calories"]
        remaining_macros = request["remaining_macros"]
        meal_type = request.get("meal_type", "dinner")
        limit = request.get("limit", 3)

        return await self.suggest_meals(
            user_id=user_id,
            remaining_calories=remaining_calories,
            remaining_macros=remaining_macros,
            meal_type=meal_type,
            limit=limit
        )

    async def suggest_meals(
        self,
        user_id: int,
        remaining_calories: int,
        remaining_macros: Dict[str, int],
        meal_type: str = "dinner",
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Generate meal suggestions.
        """
        suggestions = []
        prefs = {}

        # Get preferences if user_agent available
        if self.user_agent:
            try:
                prefs_resp = await self.user_agent.process({
                    "action": "get_preferences",
                    "user_id": user_id
                })
                prefs = prefs_resp
            except:
                prefs = {}

        # Build query for knowledge base
        query = self._build_query(
            meal_type, remaining_calories, remaining_macros, prefs
        )

        # Get recipes from knowledge
        if self.knowledge_agent:
            try:
                resp = await self.knowledge_agent.process({"query": query})
                text = resp.get("response", "")
                suggestions = self.parse_knowledge_response(text)
            except Exception as e:
                suggestions = []
        else:
            # Fallback placeholder - in production should have recipe database
            suggestions = [{
                "name": "Placeholder Meal",
                "ingredients": ["chicken", "rice", "vegetables"],
                "instructions": ["Cook chicken", "Serve with rice"],
                "nutrition": {
                    "calories": remaining_calories // 2,
                    "protein": remaining_macros.get("protein", 30) // 2,
                    "carbs": remaining_macros.get("carbs", 50) // 2,
                    "fat": remaining_macros.get("fat", 20) // 2,
                },
                "prep_time_minutes": 15,
                "cook_time_minutes": 20,
                "equipment": prefs.get("cooking_equipment", ["stove"])
            }]

        if suggestions:
            # Rank and diversify
            scored = rank_suggestions(suggestions, remaining_macros, prefs)
            ranked = diversify_suggestions(scored)
            final = ranked[:limit]
        else:
            final = []

        return {
            "suggestions": final,
            "remaining_calories": remaining_calories,
            "remaining_macros": remaining_macros
        }

    def _build_query(
        self,
        meal_type: str,
        calories: int,
        macros: Dict[str, int],
        prefs: Dict[str, Any]
    ) -> str:
        parts = [
            f"Suggest {meal_type} recipes with ~{calories} calories",
            f"~{macros.get('protein', 0)}g protein, ~{macros.get('carbs', 0)}g carbs, ~{macros.get('fat', 0)}g fat"
        ]
        if prefs.get('dietary_restrictions'):
            parts.append(f"suitable for: {', '.join(prefs['dietary_restrictions'])}")
        if prefs.get('cooking_equipment'):
            parts.append(f"using: {', '.join(prefs['cooking_equipment'])}")
        if prefs.get('favorite_foods'):
            parts.append(f"include: {', '.join(prefs['favorite_foods'][:5])}")
        if prefs.get('prep_time_max'):
            parts.append(f"prep under {prefs['prep_time_max']} minutes")
        parts.append("Provide ingredients, instructions, nutrition facts.")
        return " ".join(parts)

    def parse_knowledge_response(self, text: str) -> list:
        """Parse raw text into meal suggestions."""
        from .parser import parse_multiple_recipes
        return parse_multiple_recipes(text)
