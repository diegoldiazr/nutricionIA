"""
Meal Planner Agent - Generates intelligent meal suggestions.

Features:
- Queries NotebookLM for grounded recipe suggestions
- Smart fallback meal database when knowledge is unavailable
- Macro-aware meal generation
- Preference matching (dietary restrictions, equipment, favorites)
- Ranking and diversification of suggestions
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent
from .ranking import rank_suggestions, diversify_suggestions
from .fallback_meals import FALLBACK_MEALS, get_meals_for_calorie_range
from core.exceptions import AgentError


class MealPlannerAgent(BaseAgent):
    """
    Generates meal suggestions based on remaining calories, macros, and preferences.

    Workflow:
    1. Fetch user preferences (dietary restrictions, equipment, favorites)
    2. Query NotebookLM for grounded recipes matching targets
    3. If unavailable or insufficient results, use intelligent fallback
    4. Rank and diversify suggestions
    """

    # Calorie ranges for fallback meals
    CALORIE_RANGES = {
        "breakfast": (300, 500),
        "lunch": (500, 750),
        "dinner": (600, 900),
        "snack": (150, 300),
    }

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
        remaining_macros = request.get("remaining_macros", {})
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

        Args:
            user_id: User ID
            remaining_calories: Target calories for this meal
            remaining_macros: Target macros {protein, carbs, fat}
            meal_type: breakfast, lunch, dinner, or snack
            limit: Maximum suggestions to return
        """
        prefs = await self._get_preferences(user_id)

        # Determine calorie target for this meal
        target_cal = self._allocate_calories(remaining_calories, meal_type)
        target_macros = self._allocate_macros(remaining_macros, meal_type)

        suggestions = []

        # Try knowledge base first
        if self.knowledge_agent:
            suggestions = await self._query_knowledge(
                meal_type, target_cal, target_macros, prefs
            )

        # Fallback to intelligent meal database
        if not suggestions:
            suggestions = self._get_fallback_meals(
                meal_type, target_cal, target_macros, prefs
            )

        # Rank and diversify
        if suggestions:
            scored = rank_suggestions(suggestions, {**target_macros, "calories": target_cal}, prefs)
            ranked = diversify_suggestions(scored)
            final = ranked[:limit]
        else:
            final = []

        return {
            "suggestions": final,
            "meal_type": meal_type,
            "target_calories": target_cal,
            "target_macros": target_macros,
            "knowledge_source": len(suggestions) > 0,
        }

    async def _get_preferences(self, user_id: int) -> Dict[str, Any]:
        """Fetch user preferences, returning defaults if unavailable."""
        if not self.user_agent:
            return self._default_preferences()

        try:
            prefs = await self.user_agent.process({
                "action": "get_preferences",
                "user_id": user_id
            })
            return self._merge_with_defaults(prefs)
        except Exception:
            return self._default_preferences()

    def _default_preferences(self) -> Dict[str, Any]:
        """Default preferences when none are set."""
        return {
            "dietary_restrictions": [],
            "favorite_foods": [],
            "disliked_foods": [],
            "cooking_equipment": ["stove", "oven"],
            "prep_time_max": 45,
            "difficulty_max": "medium",
        }

    def _merge_with_defaults(self, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user prefs with defaults."""
        defaults = self._default_preferences()
        return {**defaults, **{k: v for k, v in prefs.items() if v}}

    def _allocate_calories(self, total: int, meal_type: str) -> int:
        """
        Allocate calorie budget for this meal based on type.

        Uses typical distribution:
        - Breakfast: 20-25% of daily remaining
        - Lunch: 30-35%
        - Dinner: 35-40%
        - Snacks: 10-15%
        """
        distributions = {
            "breakfast": 0.22,
            "lunch": 0.33,
            "dinner": 0.35,
            "snack": 0.10,
        }
        pct = distributions.get(meal_type, 0.33)
        allocated = int(total * pct)
        return max(200, min(allocated, total))

    def _allocate_macros(
        self, remaining_macros: Dict[str, int], meal_type: str
    ) -> Dict[str, int]:
        """
        Allocate macro targets for this meal proportionally.
        """
        distributions = {
            "breakfast": 0.22,
            "lunch": 0.33,
            "dinner": 0.35,
            "snack": 0.10,
        }
        pct = distributions.get(meal_type, 0.33)
        return {
            "protein": max(10, int(remaining_macros.get("protein", 100) * pct)),
            "carbs": max(15, int(remaining_macros.get("carbs", 150) * pct)),
            "fat": max(5, int(remaining_macros.get("fat", 50) * pct)),
        }

    async def _query_knowledge(
        self,
        meal_type: str,
        target_cal: int,
        target_macros: Dict[str, int],
        prefs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Query NotebookLM for recipes matching targets."""
        query = self._build_query(meal_type, target_cal, target_macros, prefs)
        try:
            resp = await self.knowledge_agent.process({"query": query})
            text = resp.get("response", "")
            if text and len(text) > 50:
                return self.parse_knowledge_response(text)
        except Exception:
            pass
        return []

    def _build_query(
        self,
        meal_type: str,
        calories: int,
        macros: Dict[str, int],
        prefs: Dict[str, Any]
    ) -> str:
        """Build a query for NotebookLM."""
        parts = [
            f"Suggest {meal_type} recipes with approximately {calories} calories",
            f"Target macros: {macros.get('protein', 0)}g protein,",
            f"{macros.get('carbs', 0)}g carbs, {macros.get('fat', 0)}g fat",
        ]
        if prefs.get('dietary_restrictions'):
            parts.append(f"Suitable for: {', '.join(prefs['dietary_restrictions'])}")
        if prefs.get('cooking_equipment'):
            parts.append(f"Use equipment available: {', '.join(prefs['cooking_equipment'])}")
        if prefs.get('favorite_foods'):
            parts.append(f"Include these favorites: {', '.join(prefs['favorite_foods'][:5])}")
        if prefs.get('prep_time_max'):
            parts.append(f"Maximum prep time: {prefs['prep_time_max']} minutes")
        parts.append("Provide recipe name, ingredients, instructions, and nutrition facts per 100g and total.")
        return " ".join(parts)

    def _get_fallback_meals(
        self,
        meal_type: str,
        target_cal: int,
        target_macros: Dict[str, int],
        prefs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get intelligent fallback meals from built-in database.

        Filters by:
        - Calorie range appropriate for meal type
        - Dietary restrictions
        - Equipment availability
        - Favorite foods boost
        """
        candidates = get_meals_for_calorie_range(
            FALLBACK_MEALS,
            target_cal,
            self.CALORIE_RANGES.get(meal_type, (300, 800))
        )

        # Apply dietary filters
        candidates = self._filter_by_dietary(candidates, prefs)

        # Apply equipment filters
        candidates = self._filter_by_equipment(candidates, prefs)

        # Boost favorites
        candidates = self._boost_favorites(candidates, prefs)

        # Adjust portions to match target calories
        for meal in candidates:
            self._adjust_portions(meal, target_cal, target_macros)

        return candidates

    def _filter_by_dietary(
        self, meals: List[Dict[str, Any]], prefs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter out meals that violate dietary restrictions."""
        restrictions = prefs.get("dietary_restrictions", [])
        if not restrictions:
            return meals

        filtered = []
        for meal in meals:
            tags = [t.lower() for t in meal.get("tags", [])]
            violations = [r for r in restrictions if r.lower() in tags]
            if not violations:
                filtered.append(meal)
        return filtered

    def _filter_by_equipment(
        self, meals: List[Dict[str, Any]], prefs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Prioritize meals matching available equipment."""
        equipment = prefs.get("cooking_equipment", [])
        if not equipment:
            return meals

        for meal in meals:
            meal_equipment = set(e.lower() for e in meal.get("equipment", []))
            available = set(e.lower() for e in equipment)
            match = meal_equipment & available
            meal["_equipment_match"] = len(match) / max(len(meal_equipment), 1)

        meals.sort(key=lambda m: m.get("_equipment_match", 0), reverse=True)
        return meals

    def _boost_favorites(
        self, meals: List[Dict[str, Any]], prefs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Boost meals containing favorite ingredients."""
        favorites = prefs.get("favorite_foods", [])
        if not favorites:
            return meals

        for meal in meals:
            ingredients_text = " ".join(meal.get("ingredients", [])).lower()
            matches = sum(1 for f in favorites if f.lower() in ingredients_text)
            meal["_favorite_boost"] = min(matches * 10, 30)

        return meals

    def _adjust_portions(
        self,
        meal: Dict[str, Any],
        target_cal: int,
        target_macros: Dict[str, int]
    ) -> None:
        """
        Adjust meal portions to match target calories while preserving macro ratios.
        """
        base_nut = meal.get("nutrition", {})
        base_cal = base_nut.get("calories", target_cal)
        if base_cal <= 0:
            base_cal = target_cal

        scale = target_cal / base_cal
        scale = max(0.5, min(scale, 2.0))  # Limit scaling to 0.5x - 2x

        meal["nutrition"] = {
            "calories": int(base_nut.get("calories", 0) * scale),
            "protein": int(base_nut.get("protein", 0) * scale),
            "carbs": int(base_nut.get("carbs", 0) * scale),
            "fat": int(base_nut.get("fat", 0) * scale),
        }

        # Scale ingredient quantities
        if scale != 1.0:
            for ing in meal.get("ingredients", []):
                if isinstance(ing, dict) and "quantity" in ing:
                    ing["quantity"] = int(ing["quantity"] * scale)

    def parse_knowledge_response(self, text: str) -> List[Dict[str, Any]]:
        """Parse raw text from NotebookLM into meal suggestions."""
        from .parser import parse_multiple_recipes
        return parse_multiple_recipes(text)
