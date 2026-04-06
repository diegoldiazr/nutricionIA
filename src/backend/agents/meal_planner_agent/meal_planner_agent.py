"""
Meal Planner Agent - Generates meal suggestions based on remaining calories, macros, user preferences.
May call KnowledgeAgent when needed for nutrition facts.
"""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from ...services.notebooklm_connector import NotebookLMConnector


class MealPlannerAgent(BaseAgent):
    """
    Generates meal suggestions based on:
    - Remaining calories
    - Remaining macros (protein, carbs, fat)
    - User preferences (dietary restrictions, favorite foods, equipment)
    - Prep time constraints
    """

    def __init__(self, agent_id: str = "meal_planner", knowledge_agent=None, db_session=None, user_agent=None):
        super().__init__(agent_id=agent_id, name="Meal Planner Agent")
        self.knowledge_agent = knowledge_agent
        self.db = db_session
        self.user_agent = user_agent

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate meal suggestions.

        Expected request:
        {
            "action": "suggest_meals",
            "user_id": int,
            "remaining_calories": int,
            "remaining_macros": {"protein": int, "carbs": int, "fat": int},
            "meal_type": "lunch" | "dinner" | "breakfast" | "snack",
            "limit": int = 3
        }
        """
        action = request.get("action", "suggest_meals")
        if action != "suggest_meals":
            raise ValueError(f"Unknown action: {action}")

        return await self.suggest_meals(
            user_id=request["user_id"],
            remaining_calories=request["remaining_calories"],
            remaining_macros=request["remaining_macros"],
            meal_type=request.get("meal_type", "lunch"),
            limit=request.get("limit", 3)
        )

    async def suggest_meals(
        self,
        user_id: int,
        remaining_calories: int,
        remaining_macros: Dict[str, int],
        meal_type: str = "lunch",
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Main method to generate meal suggestions.

        Returns:
            {
                "suggestions": [
                    {
                        "name": str,
                        "ingredients": List[str],
                        "instructions": List[str],
                        "nutrition": {"calories": int, "protein": int, "carbs": int, "fat": int},
                        "prep_time_minutes": int,
                        "cook_time_minutes": int,
                        "equipment": List[str]
                    }
                ],
                "remaining_calories": int,
                "remaining_macros": Dict
            }
        """
        suggestions = []

        try:
            # Get user preferences (via UserAgent if available)
            if self.user_agent:
                pref_request = {"action": "get_preferences", "user_id": user_id}
                prefs = await self.user_agent.process(pref_request)
            else:
                prefs = {}

            # Build query for NotebookLM
            query = self._build_query(
                meal_type, remaining_calories, remaining_macros, prefs
            )

            # If we have KnowledgeAgent, use it to get grounded meal ideas
            if self.knowledge_agent:
                response = await self.knowledge_agent.process({
                    "query": query,
                    "context": prefs
                })
                suggestions = self._parse_response(response.get("response", ""))
            else:
                # Fallback placeholder
                suggestions = [
                    {
                        "name": "Sample Meal",
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
                    }
                ]

            # Filter and rank
            scored = self._rank_suggestions(suggestions, remaining_macros, prefs)
            final = scored[:limit]

        except Exception as e:
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
            f"Suggest {meal_type} recipes with approximately {calories} calories",
            f"with about {macros.get('protein', 0)}g protein, {macros.get('carbs', 0)}g carbs, {macros.get('fat', 0)}g fat"
        ]
        if prefs.get('dietary_restrictions'):
            parts.append(f"suitable for: {', '.join(prefs['dietary_restrictions'])}")
        if prefs.get('cooking_equipment'):
            parts.append(f"using: {', '.join(prefs['cooking_equipment'])}")
        if prefs.get('favorite_foods'):
            parts.append(f"include some of: {', '.join(prefs['favorite_foods'][:5])}")
        if prefs.get('prep_time_max'):
            parts.append(f"under {prefs['prep_time_max']} minutes prep time")
        parts.append("Provide ingredients, instructions, and detailed nutrition facts.")
        return " ".join(parts)

    def _parse_response(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse NotebookLM response into structured meal data.
        This is a simple parser - will improve.
        """
        # Split by double newlines to identify separate recipes
        blocks = text.split('\n\n')
        meals = []
        for block in blocks:
            meal = self._parse_recipe_block(block)
            if meal:
                meals.append(meal)
        return meals

    def _parse_recipe_block(self, text: str) -> Optional[Dict[str, Any]]:
        lines = text.strip().split('\n')
        if not lines:
            return None
        name = lines[0].strip().strip('*#\'"')
        ingredients, instructions, nutrition = [], [], {}
        current_section = None
        for line in lines[1:]:
            low = line.lower().strip()
            if 'ingredient' in low:
                current_section = 'ingredients'
                continue
            if 'instruction' in low or 'step' in low:
                current_section = 'instructions'
                continue
            if 'nutrition' in low or 'calorie' in low:
                current_section = 'nutrition'
                continue
            if current_section == 'ingredients' and line.strip():
                ingredients.append(line.strip('- ').strip())
            elif current_section == 'instructions' and line.strip():
                instructions.append(line.strip('- ').strip())
            elif current_section == 'nutrition' and ':' in line:
                k, v = line.split(':', 1)
                nutrition[k.strip().lower()] = v.strip()
        if not name or not ingredients:
            return None
        # Extract numeric nutrition
        try:
            cal = int(str(nutrition.get('calories', 0)).split()[0])
        except:
            cal = 0
        try:
            prot = int(str(nutrition.get('protein', 0)).split()[0])
        except:
            prot = 0
        try:
            carb = int(str(nutrition.get('carbs', 0)).split()[0])
        except:
            carb = 0
        try:
            fat = int(str(nutrition.get('fat', 0)).split()[0])
        except:
            fat = 0
        return {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "nutrition": {"calories": cal, "protein": prot, "carbs": carb, "fat": fat},
            "prep_time_minutes": 0,
            "cook_time_minutes": 0,
            "equipment": []
        }

    def _rank_suggestions(
        self,
        meals: List[Dict[str, Any]],
        remaining_macros: Dict[str, int],
        prefs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simple ranking by preference match."""
        scored = []
        for meal in meals:
            score = 0
            # Prefer meals that are closer to macro targets
            nut = meal['nutrition']
            score += max(0, 100 - abs(nut['calories'] - remaining_macros.get('calories', 500)))
            # Favorite ingredients bonus
            meal_text = ' '.join(meal['ingredients']).lower()
            for fav in prefs.get('favorite_foods', []):
                if fav.lower() in meal_text:
                    score += 20
            scored.append((score, meal))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for s, m in scored]
