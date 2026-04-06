"""
Progress Agent - Analyzes weekly user progress.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from .analysis import calculate_weight_trend, analyze_calorie_adherence, calculate_weekly_summary
from core.exceptions import AgentError


class ProgressAgent(BaseAgent):
    """Analyze weight trends, calorie adherence, and provide feedback."""

    def __init__(
        self,
        agent_id: str = "progress",
        user_agent=None,
        nutrition_agent=None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Progress Agent", event_bus=event_bus)
        self.user_agent = user_agent
        self.nutrition_agent = nutrition_agent

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "analyze")
        if action == "analyze":
            return await self.analyze(request)
        else:
            raise AgentError(f"Unknown action: {action}")

    async def analyze(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        days = request.get("days", 7)

        # Get weight history
        weight_history = []
        if self.user_agent:
            try:
                wh_resp = await self.user_agent.process({
                    "action": "get_weight_history",
                    "user_id": user_id,
                    "days": days
                })
                weight_history = wh_resp.get("weight_history", [])
            except:
                weight_history = []

        # Get profile for targets
        profile = {}
        if self.user_agent:
            try:
                profile = await self.user_agent.process({
                    "action": "get_profile",
                    "user_id": user_id
                })
            except:
                pass

        # Get daily macros
        daily_macros = []
        if self.user_agent:
            from datetime import date, timedelta
            target_date = date.today()
            for i in range(days):
                d = target_date - timedelta(days=i)
                try:
                    macro_resp = await self.user_agent.process({
                        "action": "get_daily_macros",
                        "user_id": user_id,
                        "date": d.isoformat()
                    })
                    if macro_resp.get("calories", 0) > 0:
                        daily_macros.append(macro_resp)
                except:
                    pass

        # Calculate targets
        target_calories = profile.get("daily_calories", 0)

        # Analyze
        weight_trend = calculate_weight_trend(weight_history, days)
        calorie_adherence = analyze_calorie_adherence(
            daily_macros, target_calories
        )
        summary = calculate_weekly_summary(
            weight_trend, calorie_adherence, request.get("training_days", 0)
        )

        return {
            "overall_score": summary["overall_score"],
            "weight_trend": weight_trend,
            "calorie_adherence": calorie_adherence,
            "summary": summary
        }
