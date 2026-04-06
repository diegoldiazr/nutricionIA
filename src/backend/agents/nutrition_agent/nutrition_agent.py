"""
Nutrition Agent - Calculates BMR, TDEE, calorie targets, macronutrient targets.
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from ...services.notebooklm_connector import NotebookLMConnector


class NutritionAgent(BaseAgent):
    """
    Physiological metric calculations.
    Validates through KnowledgeAgent when needed.
    """

    def __init__(self, agent_id: str = "nutrition", knowledge_agent=None, db_session=None):
        super().__init__(agent_id=agent_id, name="Nutrition Agent")
        self.knowledge_agent = knowledge_agent
        self.db = db_session

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route nutrition requests.

        Request types:
        - calculate_bmr: {"action":"calculate_bmr","weight":float,"height":float,"age":int,"gender":str}
        - calculate_tdee: {"action":"calculate_tdee","bmr":float,"activity_level":str}
        - calculate_targets: {"action":"calculate_targets","profile":Dict}
        - validate_macros: {"action":"validate_macros","macros":Dict,"context":Dict}
        """
        action = request.get("action")
        if not action:
            raise ValueError("Action is required")

        handlers = {
            "calculate_bmr": self._handle_calculate_bmr,
            "calculate_tdee": self._handle_calculate_tdee,
            "calculate_targets": self._handle_calculate_targets,
            "validate_macros": self._handle_validate_macros,
        }

        if action not in handlers:
            raise ValueError(f"Unknown action: {action}")

        return await handlers[action](request)

    async def _handle_calculate_bmr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        weight = request["weight"]
        height = request["height"]
        age = request["age"]
        gender = request["gender"]

        bmr = self.calculate_bmr(weight, height, age, gender)
        return {
            "method": "Harris-Benedict",
            "bmr": round(bmr, 2),
            "inputs": {"weight": weight, "height": height, "age": age, "gender": gender}
        }

    async def _handle_calculate_tdee(self, request: Dict[str, Any]) -> Dict[str, Any]:
        bmr = request["bmr"]
        activity_level = request["activity_level"]

        tdee = self.calculate_tdee(bmr, activity_level)
        return {
            "tdee": round(tdee, 2),
            "bmr": bmr,
            "activity_level": activity_level,
            "multiplier": self._activity_multipliers.get(activity_level, 1.55)
        }

    async def _handle_calculate_targets(self, request: Dict[str, Any]) -> Dict[str, Any]:
        profile = request["profile"]
        weight = profile.get("weight_current", 75)
        height = profile.get("height", 175)
        age = profile.get("age", 30)
        gender = profile.get("gender", "male")
        activity_level = profile.get("activity_level", "moderate")
        goal = profile.get("goal", "maintain")

        bmr = self.calculate_bmr(weight, height, age, gender)
        tdee = self.calculate_tdee(bmr, activity_level)
        macros = self.calculate_macros(weight, tdee, goal, activity_level)

        result = {
            "bmr": round(bmr, 2),
            "tdee": round(tdee, 2),
            "activity_multiplier": self._activity_multipliers.get(activity_level, 1.55),
            "daily_calories": macros["calories"],
            "macro_breakdown": macros,
        }

        # Optionally validate through KnowledgeAgent
        if self.knowledge_agent:
            validation = await self._validate_via_knowledge(macros, profile)
            result["knowledge_validation"] = validation

        return result

    async def _handle_validate_macros(self, request: Dict[str, Any]) -> Dict[str, Any]:
        macros = request["macros"]
        context = request.get("context", {})
        return await self._validate_via_knowledge(macros, context)

    # --- Core calculation methods ---

    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        if gender.lower() in ('male', 'm'):
            return 66.47 + (13.75 * weight) + (5.003 * height) - (6.755 * age)
        else:
            return 655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age)

    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        return bmr * self._activity_multipliers.get(activity_level, 1.55)

    def calculate_macros(self, weight: float, tdee: float, goal: str, activity_level: str = None) -> Dict[str, int]:
        if goal == 'lose_weight':
            calories = tdee - 500
        elif goal == 'gain_muscle':
            calories = tdee + 300
        else:
            calories = tdee

        protein_per_kg = 2.0 if goal == 'lose_weight' else 1.8 if goal == 'gain_muscle' else 1.6
        protein_grams = weight * protein_per_kg
        fat_grams = (calories * 0.25) / 9
        protein_calories = protein_grams * 4
        fat_calories = fat_grams * 9
        carbs_grams = max(0, (calories - protein_calories - fat_calories) / 4)

        total_cal = protein_calories + (fat_grams * 9) + (carbs_grams * 4)
        return {
            'calories': int(calories),
            'protein_grams': int(protein_grams),
            'carbs_grams': int(carbs_grams),
            'fat_grams': int(fat_grams),
            'protein_percentage': round((protein_calories / total_cal) * 100, 1) if total_cal else 0,
            'fat_percentage': round(((fat_grams * 9) / total_cal) * 100, 1) if total_cal else 0,
            'carbs_percentage': round(((carbs_grams * 4) / total_cal) * 100, 1) if total_cal else 0,
        }

    # --- Helper ---

    _activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9,
    }

    async def _validate_via_knowledge(self, macros: Dict, profile: Dict) -> Dict[str, Any]:
        """Validate macros through KnowledgeAgent."""
        if not self.knowledge_agent:
            return {"status": "skipped", "reason": "no knowledge agent available"}
        try:
            query = (
                f"Are these macros reasonable for goal={profile.get('goal','maintain')}?"
            )
            result = await self.knowledge_agent.process({"query": query})
            return {"status": "validated", "knowledge_response": result.get("response", "")}
        except Exception as e:
            return {"status": "error", "error": str(e)}
