"""
Recommendation Agent - Generates high level coaching recommendations.
"""

from typing import Dict, Any, List
from ..base_agent import BaseAgent
from core.exceptions import AgentError


class RecommendationAgent(BaseAgent):
    """
    Produces coaching recommendations based on:
    - Nutrition targets
    - Progress analysis
    - User profile
    - Memory patterns
    """

    def __init__(
        self,
        agent_id: str = "recommendation",
        nutrition_agent=None,
        progress_agent=None,
        user_agent=None,
        memory_agent=None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Recommendation Agent", event_bus=event_bus)
        self.nutrition_agent = nutrition_agent
        self.progress_agent = progress_agent
        self.user_agent = user_agent
        self.memory_agent = memory_agent

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "generate")
        if action == "generate":
            return await self.generate(request)
        else:
            raise AgentError(f"Unknown action: {action}")

    async def generate(self, request: Dict[str, Any]) -> Dict[str, Any]:
        user_id = request["user_id"]
        days = request.get("days", 7)

        recommendations = []

        # Get progress analysis
        progress = None
        if self.progress_agent:
            try:
                progress = await self.progress_agent.process({
                    "action": "analyze",
                    "user_id": user_id,
                    "days": days
                })
            except:
                pass

        # Get user profile
        profile = {}
        if self.user_agent:
            try:
                profile = await self.user_agent.process({
                    "action": "get_profile",
                    "user_id": user_id
                })
            except:
                pass

        # Get nutrition targets
        targets = profile
        if self.nutrition_agent:
            try:
                targets = await self.nutrition_agent.process({
                    "action": "calculate_targets",
                    "profile": profile
                })
            except:
                pass

        # Generate recommendations from progress
        if progress:
            score = progress.get("overall_score", 0)
            if score < 50:
                recommendations.append(
                    "Consider adjusting your calorie intake. Your adherence could be better."
                )
                recommendations.append(
                    "Try to maintain more consistent meal times for better results."
                )
            elif score < 75:
                recommendations.append(
                    "Good progress! Consider increasing protein intake by 10-15g per day."
                )
            else:
                recommendations.append(
                    "Excellent progress! Keep your current routine. Consider a refeed day."
                )

            # Trend-based recommendations
            trend = progress.get("weight_trend", {}).get("trend", "unknown")
            if trend == "stable":
                recommendations.append(
                    "Your weight is stable. Consider slight deficit if losing weight is the goal."
                )
            elif trend == "up":
                recommendations.append(
                    "Slight weight increase detected. Reduce daily calories by ~200 kcal."
                )
            elif trend == "down":
                recommendations.append(
                    "Good weight trend. Make sure you're losing weight gradually (0.5-1kg/week)."
                )

        # Get memory-based patterns if available
        memory = {}
        if self.memory_agent:
            try:
                memory = await self.memory_agent.process({
                    "action": "get_patterns",
                    "user_id": user_id
                })
            except:
                pass

        if memory.get("hunger_patterns"):
            recommendations.append(
                "Based on your hunger patterns, consider a larger breakfast and lighter dinner."
            )

        # Fallback if no progress yet
        if not recommendations:
            recommendations.append(
                "Not enough data yet. Keep logging your meals and we'll provide personalized recommendations soon."
            )

        return {
            "recommendations": recommendations,
            "overall_feedback": " ".join(recommendations),
            "score": progress.get("overall_score", 0) if progress else 0
        }
