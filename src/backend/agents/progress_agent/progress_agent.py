"""
Progress Agent - Analyzes weekly user progress.
Inputs: weight change, calorie intake, training
Outputs: feedback, adjustment suggestions
"""
from typing import Dict, Any
from datetime import date, timedelta
from .base_agent import BaseAgent


class ProgressAgent(BaseAgent):
    """
    Analyzes weekly user progress by combining:
    - Weight change trends
    - Calorie intake vs targets
    - Training adherence
    - Energy levels
    """

    def __init__(self, agent_id: str = "progress", user_agent=None, nutrition_agent=None):
        super().__init__(agent_id=agent_id, name="Progress Agent")
        self.user_agent = user_agent
        self.nutrition_agent = nutrition_agent

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "analyze")
        if action == "analyze":
            user_id = request["user_id"]
            days = request.get("days", 7)
            return await self.analyze_progress(user_id, days)
        elif action == "trend":
            user_id = request["user_id"]
            metric = request.get("metric", "weight")
            return await self.get_trend(user_id, metric)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def analyze_progress(self, user_id: int, lookback_days: int = 7) -> Dict[str, Any]:
        """
        Core analysis method.

        Returns:
            {
                "weight_change_weekly": float,  # grams
                "weight_trend": "up|down|stable",
                "avg_daily_calories": int,
                "avg_protein_per_kg": float,
                "adherence_rate": float,
                "training_days": int,
                "hunger_patterns": Dict,
                "days_with_weight": int,
                "current_calorie_target": int,
            }
        """
        analysis = {
            "weight_change_weekly": 0,
            "weight_trend": "stable",
            "avg_daily_calories": 0,
            "avg_protein_per_kg": 0,
            "adherence_rate": 0.0,
            "training_days": 0,
            "hunger_patterns": {
                "late_night_hunger": False,
                "mid_morning_crash": False,
            },
            "days_with_weight": 0,
            "current_calorie_target": 0,
        }

        try:
            # Get user profile for weight
            if self.user_agent:
                profile = await self.user_agent.process({"action": "get_profile", "user_id": user_id})
                current_weight = profile.get("weight_current", 75)
                goal = profile.get("goal", "maintain")
            else:
                current_weight = 75
                goal = "maintain"

            # Get weight history
            if self.user_agent:
                hist_req = {"action": "get_weight_history", "user_id": user_id, "days": lookback_days}
                hist_resp = await self.user_agent.process(hist_req)
                entries = hist_resp.get("entries", [])
            else:
                entries = []

            if len(entries) >= 2:
                start_w = entries[0]["weight"]
                end_w = entries[-1]["weight"]
                change_g = (end_w - start_w) * 1000
                if lookback_days > 0:
                    weekly_change = change_g * (7 / lookback_days)
                else:
                    weekly_change = 0
                analysis["weight_change_weekly"] = round(weekly_change, 1)
                analysis["weight_trend"] = "down" if weekly_change < -50 else "up" if weekly_change > 50 else "stable"
                analysis["days_with_weight"] = len(entries)

            # Calculate targets
            if self.nutrition_agent:
                # Call NutritionAgent to calculate targets (would need height, age, etc)
                # This is a simplified placeholder
                analysis["current_calorie_target"] = 2200 if goal == "lose_weight" else 2500
            else:
                analysis["current_calorie_target"] = 2200

            # Placeholder adherence (would come from meal logging completeness)
            analysis["adherence_rate"] = 0.75
            analysis["avg_daily_calories"] = int(analysis["current_calorie_target"] * analysis["adherence_rate"])
            analysis["avg_protein_per_kg"] = 1.7 if goal == "lose_weight" else 1.5

        except Exception as e:
            print(f"Error analyzing progress: {e}")

        return analysis

    async def get_trend(self, user_id: int, metric: str = "weight") -> Dict[str, Any]:
        """Get trend for a specific metric over time."""
        if metric == "weight":
            if self.user_agent:
                hist = await self.user_agent.process({
                    "action": "get_weight_history",
                    "user_id": user_id,
                    "days": 30
                })
                entries = hist.get("entries", [])
                if len(entries) >= 2:
                    start = entries[0]["weight"]
                    end = entries[-1]["weight"]
                    change = end - start
                    avg_change = change / max(1, len(entries)-1)
                    return {
                        "metric": "weight",
                        "change_total_kg": round(change, 2),
                        "avg_daily_change_kg": round(avg_change, 3),
                        "trend": "down" if change < -0.5 else "up" if change > 0.5 else "stable"
                    }
        return {"metric": metric, "trend": "unknown", "reason": "insufficient data"}
