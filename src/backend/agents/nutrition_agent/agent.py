"""
Nutrition Agent - Calculates BMR, TDEE, calorie targets, macronutrient targets.

Now uses pure calculation functions from formulas.py.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from .formulas import (
    calculate_bmr,
    calculate_tdee,
    calculate_macros,
    calculate_remaining_macros,
    ACTIVITY_MULTIPLIERS
)
from core.events import EventType
from core.exceptions import AgentError


class NutritionAgent(BaseAgent):
    """
    Physiological metric calculations.

    Uses pure math functions - no external API calls.
    Optional knowledge validation via events.
    """

    def __init__(
        self,
        agent_id: str = "nutrition",
        event_bus=None,
        openrouter_service=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Nutrition Agent", event_bus=event_bus)
        self.openrouter = openrouter_service
        # Accept but ignore knowledge_agent for now (validation via event bus)

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route nutrition requests.

        Actions:
        - calculate_all: Given profile, compute all metrics
        - calculate_bmr: BMR only
        - calculate_tdee: TDEE given BMR and activity
        - calculate_targets: Full target calculation
        """
        action = request.get("action")
        if not action:
            raise AgentError("Action is required")

        handlers = {
            "calculate_bmr": self._handle_bmr,
            "calculate_tdee": self._handle_tdee,
            "calculate_targets": self._handle_targets,
        }

        if action not in handlers:
            raise AgentError(f"Unknown action: {action}")

        result = await handlers[action](request)

        # Publish event
        if self.event_bus:
            self.event_bus.publish(EventType.TARGETS_CALCULATED, {
                'user_id': request.get('user_id'),
                'action': action,
                'result': result
            })

        return result

    async def _handle_bmr(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate BMR from request parameters."""
        weight = request["weight"]
        height = request["height"]
        age = request["age"]
        gender = request["gender"]

        bmr = calculate_bmr(weight, height, age, gender)
        return {
            "method": "Harris-Benedict",
            "bmr": round(bmr, 2),
            "inputs": {"weight": weight, "height": height, "age": age, "gender": gender}
        }

    async def _handle_tdee(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate TDEE from BMR and activity level."""
        bmr = request["bmr"]
        activity_level = request["activity_level"]
        tdee = calculate_tdee(bmr, activity_level)
        return {
            "tdee": round(tdee, 2),
            "bmr": bmr,
            "activity_level": activity_level,
            "multiplier": ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        }

    async def _handle_targets(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate full targets from profile."""
        profile = request["profile"]
        weight = profile.get("weight_current", 75)
        height = profile.get("height", 175)
        age = profile.get("age", 30)
        gender = profile.get("gender", "male")
        activity_level = profile.get("activity_level", "moderate")
        goal = profile.get("goal", "maintain")

        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity_level)
        macros = calculate_macros(weight, tdee, goal, activity_level)

        result = {
            "bmr": round(bmr, 2),
            "tdee": round(tdee, 2),
            "activity_multiplier": ACTIVITY_MULTIPLIERS.get(activity_level, 1.55),
            "daily_calories": macros["calories"],
            "macro_breakdown": macros,
        }

        # Optional validation - skipped for now (via event bus)
        return result
