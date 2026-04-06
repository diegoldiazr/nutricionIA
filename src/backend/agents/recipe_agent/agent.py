"""
Recipe Agent - Generates complete recipes.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from .parser import parse_multiple_recipes, extract_cooking_equipment, estimate_prep_time
from core.events import EventType
from core.exceptions import AgentError


class RecipeAgent(BaseAgent):
    """Specialized agent for generating recipes."""

    def __init__(
        self,
        agent_id: str = "recipe",
        knowledge_agent=None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Recipe Agent", event_bus=event_bus)
        self.knowledge_agent = knowledge_agent

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "generate_recipe")
        if action == "generate_recipe":
            return await self.generate_recipe(request)
        elif action == "get_recipe_by_ingredients":
            return await self.get_recipe_by_ingredients(request)
        else:
            raise AgentError(f"Unknown action: {action}")

    async def generate_recipe(self, request: Dict[str, Any]) -> Dict[str, Any]:
        constraints = request.get("constraints", {})
        query = self._build_query(constraints)

        response_text = ""
        if self.knowledge_agent:
            resp = await self.knowledge_agent.process({"query": query})
            response_text = resp.get("response", "")

        from .parser import parse_multiple_recipes, extract_cooking_equipment, estimate_prep_time
        recipes = parse_multiple_recipes(response_text)

        for recipe in recipes:
            if not recipe.get('equipment'):
                recipe['equipment'] = extract_cooking_equipment(response_text)
            if recipe.get('prep_time_minutes', 0) == 0:
                recipe['prep_time_minutes'] = estimate_prep_time(
                    len(recipe.get('ingredients', [])),
                    len(recipe.get('instructions', []))
                )

        return {"recipes": recipes[:3], "query": query}

    async def get_recipe_by_ingredients(self, request: Dict[str, Any]) -> Dict[str, Any]:
        ingredients = request.get("ingredients", [])
        query = f"Find recipes using: {', '.join(ingredients)}"
        response_text = ""
        if self.knowledge_agent:
            resp = self.knowledge_agent.process({"query": query})
            response_text = resp.get("response", "")
        from .parser import parse_multiple_recipes
        return {"recipes": parse_multiple_recipes(response_text)}

    def _build_query(self, constraints: Dict[str, Any]) -> str:
        parts = []
        if cuisine := constraints.get("cuisine"):
            parts.append(f"Generate {cuisine} recipe")
        if calories := constraints.get("calories"):
            parts.append(f"with ~{calories} calories")
        if macros := constraints.get("macros", {}):
            p = macros.get("protein", 0)
            c = macros.get("carbs", 0)
            f = macros.get("fat", 0)
            parts.append(f"macros: {p}g protein, {c}g carbs, {f}g fat")
        if equipment := constraints.get("equipment", []):
            parts.append(f"using: {', '.join(equipment)}")
        if main := constraints.get("main_ingredient"):
            parts.append(f"main ingredient: {main}")
        if dietary := constraints.get("dietary_restrictions", []):
            parts.append(f"suitable for: {', '.join(dietary)}")
        parts.append("Include full ingredients list and step-by-step instructions.")
        return " ".join(parts)
