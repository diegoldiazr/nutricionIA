"""
Recommendation Agent - High level coaching recommendations.
Analyzes progress and provides actionable advice.
"""
from typing import Dict, Any, List
from datetime import date
from .base_agent import BaseAgent


class RecommendationAgent(BaseAgent):
    """
    Produces high-level coaching recommendations:
    - Adjust calorie targets
    - Modify protein intake
    - Change meal timing
    - Suggest new strategies
    """

    def __init__(self, agent_id: str = "recommendation", nutrition_agent=None, progress_agent=None, user_agent=None, memory_agent=None):
        super().__init__(agent_id=agent_id, name="Recommendation Agent")
        self.nutrition_agent = nutrition_agent
        self.progress_agent = progress_agent
        self.user_agent = user_agent
        self.memory_agent = memory_agent

    async def initialize(self) -> None:
        await super().initialize()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "generate")
        if action == "generate":
            user_id = request["user_id"]
            days = request.get("days", 7)
            return await self.generate_recommendations(user_id, days)
        elif action == "quick_feedback":
            user_id = request["user_id"]
            return await self.quick_feedback(user_id)
        else:
            raise ValueError(f"Unknown action: {action}")

    async def generate_recommendations(self, user_id: int, lookback_days: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive coaching recommendations.

        Returns:
            {
                "calorie_adjustment": {...},
                "macro_adjustment": {...},
                "meal_timing": {...},
                "food_suggestions": [...],
                "overall_feedback": str,
                "confidence_score": float
            }
        """
        recommendations = {
            "calorie_adjustment": None,
            "macro_adjustment": None,
            "meal_timing": {},
            "food_suggestions": [],
            "overall_feedback": "",
            "confidence_score": 0.0,
        }

        try:
            # Get progress analysis
            if self.progress_agent:
                progress = await self.progress_agent.process({
                    "action": "analyze",
                    "user_id": user_id,
                    "days": lookback_days
                })
            else:
                progress = {}

            # Get user profile
            if self.user_agent:
                profile = await self.user_agent.process({"action": "get_profile", "user_id": user_id})
            else:
                profile = {"goal": "maintain", "weight_current": 75}

            # 1. Calorie recommendation
            if progress.get("weight_change_weekly") is not None:
                recommendations["calorie_adjustment"] = self._recommend_calorie_adjustment(
                    progress["weight_change_weekly"],
                    progress.get("current_calorie_target", 2200),
                    profile.get("goal", "maintain")
                )

            # 2. Macro recommendation
            recommendations["macro_adjustment"] = self._recommend_macro_adjustment(
                progress, profile
            )

            # 3. Meal timing
            recommendations["meal_timing"] = self._recommend_meal_timing(progress, profile)

            # 4. Food suggestions from memory or preferences
            if self.memory_agent:
                mem = await self.memory_agent.process({"action": "get_suggestions", "user_id": user_id})
                recommendations["food_suggestions"] = mem.get("suggestions", [])

            # 5. Overall feedback
            recommendations["overall_feedback"] = self._generate_overall_feedback(progress, recommendations)
            recommendations["confidence_score"] = self._calc_confidence(progress, profile)

        except Exception as e:
            recommendations["overall_feedback"] = f"Unable to generate full recommendations: {str(e)}"

        return recommendations

    def _recommend_calorie_adjustment(self, weight_change_g: float, current_target: int, goal: str) -> Dict[str, Any]:
        """Adjust based on weekly weight change."""
        change_kg = weight_change_g / 1000
        if goal == 'lose_weight':
            if change_kg < -0.5:  # losing too fast
                return {"adjustment": "increase", "amount": 150, "reason": f"Losing too fast ({abs(change_kg):.1f} kg/week). Increase calories to slow loss."}
            elif change_kg > 0.1:  # gaining
                return {"adjustment": "decrease", "amount": 200, "reason": f"Gaining weight ({change_kg:.1f} kg/week). Reduce calories."}
            else:
                return {"adjustment": "maintain", "amount": 0, "reason": "Weight loss on track."}
        elif goal == 'gain_muscle':
            if change_kg < 0.1:
                return {"adjustment": "increase", "amount": 200, "reason": f"Weight gain too slow ({change_kg:.1f} kg/week). Add calories."}
            elif change_kg > 0.5:
                return {"adjustment": "decrease", "amount": 150, "reason": f"Gaining too fast ({change_kg:.1f} kg/week). Reduce to minimize fat."}
            else:
                return {"adjustment": "maintain", "amount": 0, "reason": "Muscle gain rate is optimal."}
        else:  # maintain
            if abs(change_kg) > 0.5:
                return {"adjustment": "adjust", "amount": 100 if change_kg > 0 else -100, "reason": f"Weight drifted {change_kg:.1f} kg. Adjust calories."}
            else:
                return {"adjustment": "maintain", "amount": 0, "reason": "Weight stable."}

    def _recommend_macro_adjustment(self, progress: Dict, profile: Dict) -> Dict[str, Any]:
        current_protein = progress.get("avg_protein_per_kg", 1.6)
        weight = profile.get("weight_current", 75)
        goal = profile.get("goal", "maintain")
        target_per_kg = 2.0 if goal == 'lose_weight' else 1.8 if goal == 'gain_muscle' else 1.6
        target_total = weight * target_per_kg
        diff = int(target_total - (current_protein * weight))
        if abs(diff) > 20:
            return {
                "adjust_protein": True,
                "change_grams": diff,
                "reason": f"Protein intake is off by ~{abs(diff)}g. {'Increase' if diff > 0 else 'Decrease'} to optimize for {goal}."
            }
        else:
            return {
                "adjust_protein": False,
                "change_grams": 0,
                "reason": f"Protein intake is optimal (~{current_protein:.1f}g/kg)."
            }

    def _recommend_meal_timing(self, progress: Dict, profile: Dict) -> Dict[str, Any]:
        patterns = progress.get("hunger_patterns", {})
        suggestions = []
        if patterns.get("late_night_hunger"):
            suggestions.append("Add a protein-rich evening snack")
        if patterns.get("mid_morning_crash"):
            suggestions.append("Ensure breakfast has adequate protein")
        if patterns.get("afternoon_slump"):
            suggestions.append("Include fiber and protein at lunch")
        return {
            "suggestions": suggestions,
            "rationale": "Based on hunger patterns." if suggestions else "Meal timing appears balanced."
        }

    def _generate_overall_feedback(self, progress: Dict, recommendations: Dict) -> str:
        adherence = progress.get("adherence_rate", 0)
        weight_change = progress.get("weight_change_weekly", 0)
        if adherence < 0.6:
            return "Adherence is low. Focus on consistency - track all meals and hit protein targets first."
        elif abs(weight_change) > 500 and recommendations.get("calorie_adjustment"):
            adj = recommendations["calorie_adjustment"]
            return f"Weight changed {abs(weight_change/1000):.1f} kg this week. {adj['reason']}"
        else:
            return "Good progress. Keep up the consistent logging and follow your macro targets."

    def _calc_confidence(self, progress: Dict, profile: Dict) -> float:
        weight_days = progress.get("days_with_weight", 0)
        adherence = progress.get("adherence_rate", 0)
        score = 0.0
        if weight_days >= 5:
            score += 0.5
        elif weight_days >= 3:
            score += 0.25
        if adherence >= 0.8:
            score += 0.5
        elif adherence >= 0.6:
            score += 0.25
        return round(score, 2)

    async def quick_feedback(self, user_id: int) -> Dict[str, Any]:
        """Same-day quick feedback."""
        return {
            "message": "Keep going! You're doing great.",
            "suggestions": ["Log your meals", "Stay hydrated"]
        }
