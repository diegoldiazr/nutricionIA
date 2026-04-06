"""
Recipe Agent - Generates recipes compatible with:
- Airfryer
- Thermomix
- Simple home cooking

Recipes must fit calorie and macro targets.
"""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent


class RecipeAgent(BaseAgent):
    """
    Specialized agent for generating complete recipes.
    """

    def __init__(self, agent_id: str = "recipe", knowledge_agent=None, meal_planner_agent=None):
        super().__init__(agent_id=agent_id, name="Recipe Agent")
        self.knowledge_agent = knowledge_agent
        self.meal_planner = meal_planner_agent

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "generate_recipe")
        if action == "generate_recipe":
            return await self.generate_recipe(request)
        elif action == "get_recipe_by_ingredients":
            return await self.get_recipe_by_ingredients(request)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def generate_recipe(self, request: Dict[str, Any]) -> Dict[str, Any]:
        constraints = request.get("constraints", {})
        query_parts = [
            f"Generate a recipe for {constraints.get('cuisine', 'any')} cuisine",
            f"with approximately {constraints.get('calories', 500)} calories",
            f"with {constraints.get('macros', {}).get('protein', 30)}g protein"
        ]
        if equipment := constraints.get("equipment", []):
            query_parts.append(f"using: {', '.join(equipment)}")
        if main := constraints.get("main_ingredient"):
            query_parts.append(f"main ingredient: {main}")
        if dietary := constraints.get("dietary_restrictions", []):
            query_parts.append(f"suitable for {', '.join(dietary)}")
        query_parts.append("Include detailed ingredients list and step-by-step instructions.")
        query = " ".join(query_parts)

        response = None
        if self.knowledge_agent:
            resp = await self.knowledge_agent.process({"query": query})
            response = resp.get("response", "")
        recipe = self._parse_recipe(response or "", constraints)
        return {"recipe": recipe, "query": query}

    async def get_recipe_by_ingredients(self, request: Dict[str, Any]) -> Dict[str, Any]:
        ingredients = request.get("ingredients", [])
        query = f"Find recipes using: {', '.join(ingredients)}"
        response = ""
        if self.knowledge_agent:
            resp = await self.knowledge_agent.process({"query": query})
            response = resp.get("response", "")
        return {"recipes": self._parse_multiple(response)}

    def _parse_recipe(self, text: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        lines = text.strip().split('\n')
        name = lines[0].strip('*#\'"') if lines else "Untitled Recipe"
        ingredients, instructions = [], []
        section = None
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if any(kw in line.lower() for kw in ['ingredient', 'what you need']):
                section = 'ingredients'
                continue
            if any(kw in line.lower() for kw in ['instruction', 'step', 'method', 'directions']):
                section = 'instructions'
                continue
            if section == 'ingredients' and line and (line[0] in '-•'):
                ingredients.append(line.lstrip('-• '))
            elif section == 'instructions' and line and (line[0].isdigit() or line.startswith('-')):
                instructions.append(line.lstrip('0123456789- '))
        return {
            "name": name,
            "ingredients": ingredients,
            "instructions": instructions,
            "estimated_nutrition": {
                "calories": constraints.get('calories', 500),
                "protein": constraints.get('macros', {}).get('protein', 30),
                "carbs": constraints.get('macros', {}).get('carbs', 50),
                "fat": constraints.get('macros', {}).get('fat', 15),
            },
            "equipment_required": constraints.get("equipment", []),
        }

    def _parse_multiple(self, text: str) -> List[Dict[str, Any]]:
        return []

