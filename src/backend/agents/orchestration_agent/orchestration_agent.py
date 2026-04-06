"""
Orchestrator Agent - Coordinates agent communication and flow.
Central controller that combines agent outputs.
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class OrchestrationAgent(BaseAgent):
    """
    Central controller that:
    - Coordinates agent communication
    - Combines results from multiple agents
    - Generates final output for frontend
    - Manages request routing
    """

    def __init__(self, agent_id: str = "orchestrator", agents: Dict[str, BaseAgent] = None):
        super().__init__(agent_id=agent_id, name="Orchestrator Agent")
        self.agents = agents or {}
        # Set orchestrator reference on all agents
        for agent in self.agents.values():
            agent.orchestrator = self

    async def initialize(self) -> None:
        """Initialize all registered agents."""
        await super().initialize()
        for agent in self.agents.values():
            await agent.initialize()
        print(f"Orchestrator initialized with {len(self.agents)} agents")

    async def shutdown(self) -> None:
        """Shutdown all agents."""
        for agent in self.agents.values():
            await agent.shutdown()
        await super().shutdown()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for all requests to the agent system.

        Request types:
        - daily_summary: {
            "action": "daily_summary",
            "user_id": int,
            "date": str
          }
        - progress_report: {
            "action": "progress_report",
            "user_id": int,
            "days": 7
          }
        - log_meal: {
            "action": "log_meal",
            "user_id": int,
            "meal_data": Dict
          }
        - recipe_suggestions: {
            "action": "recipe_suggestions",
            "user_id": int,
            "constraints": Dict
          }
        - get_recommendations: {
            "action": "get_recommendations",
            "user_id": int,
            "days": 7
          }
        """
        action = request.get("action", "")
        if not action:
            raise ValueError("Action is required")

        # Route to appropriate workflow
        if action == "daily_summary":
            return await self.workflow_daily_summary(
                user_id=request["user_id"],
                date_str=request.get("date")
            )
        elif action == "progress_report":
            return await self.workflow_progress_report(
                user_id=request["user_id"],
                days=request.get("days", 7)
            )
        elif action == "log_meal":
            return await self.workflow_log_meal(
                user_id=request["user_id"],
                meal_data=request["meal_data"]
            )
        elif action == "recipe_suggestions":
            return await self.workflow_recipe_suggestions(
                user_id=request["user_id"],
                constraints=request.get("constraints", {})
            )
        elif action == "get_recommendations":
            return await self.workflow_get_recommendations(
                user_id=request["user_id"],
                days=request.get("days", 7)
            )
        else:
            # For direct agent access (e.g., /api/v1 routes that bypass orchestrator)
            return await self._handle_direct_action(request)

    # ==================== Workflows ====================

    async def workflow_daily_summary(self, user_id: int, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate daily summary combining:
        - User profile & daily macros
        - Nutrition targets
        - Meal suggestions for remaining macros
        - Memory patterns update
        """
        from datetime import date
        target_date = date_str or date.today().isoformat()
        summary = {
            "user_id": user_id,
            "date": target_date,
            "nutrition_status": {},
            "meal_suggestions": [],
            "daily_macros": None
        }

        # 1. Get user profile
        user_agent = self.agents.get("user")
        if not user_agent:
            raise ValueError("User agent not registered")

        profile = await user_agent.process({"action": "get_profile", "user_id": user_id})
        summary["profile"] = profile

        # 2. Get daily macros
        macros_response = await user_agent.process({
            "action": "get_daily_macros",
            "user_id": user_id,
            "date": target_date
        })
        summary["daily_macros"] = macros_response

        # 3. Calculate targets via NutritionAgent
        nutrition_agent = self.agents.get("nutrition")
        if nutrition_agent:
            targets_resp = await nutrition_agent.process({
                "action": "calculate_targets",
                "profile": profile
            })
            summary["nutrition_status"]["targets"] = targets_resp

            # Compute remaining
            consumed = macros_response
            targets = targets_resp
            remaining = {
                "calories": max(0, targets["daily_calories"] - consumed.get("calories", 0)),
                "protein": max(0, targets["macro_breakdown"]["protein_grams"] - consumed.get("protein", 0)),
                "carbs": max(0, targets["macro_breakdown"]["carbs_grams"] - consumed.get("carbs", 0)),
                "fat": max(0, targets["macro_breakdown"]["fat_grams"] - consumed.get("fat", 0)),
            }
            summary["nutrition_status"]["remaining"] = remaining

            # 4. Get meal suggestions if needed
            if remaining["calories"] > 100:
                meal_planner = self.agents.get("meal_planner")
                if meal_planner:
                    suggestions = await meal_planner.process({
                        "action": "suggest_meals",
                        "user_id": user_id,
                        "remaining_calories": remaining["calories"],
                        "remaining_macros": remaining,
                        "meal_type": "dinner"
                    })
                    summary["meal_suggestions"] = suggestions.get("suggestions", [])

        return summary

    async def workflow_progress_report(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Generate weekly progress report:
        - Progress analysis
        - Recommendations
        """
        report = {"user_id": user_id, "period_days": days}

        # Get progress
        progress_agent = self.agents.get("progress")
        if progress_agent:
            progress = await progress_agent.process({
                "action": "analyze",
                "user_id": user_id,
                "days": days
            })
            report["progress_analysis"] = progress

        # Get recommendations
        rec_agent = self.agents.get("recommendation")
        if rec_agent:
            recs = await rec_agent.process({
                "action": "generate",
                "user_id": user_id,
                "days": days
            })
            report["recommendations"] = recs
            report["summary"] = recs.get("overall_feedback", "")

        return report

    async def workflow_log_meal(self, user_id: int, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a meal logging:
        - Record via UserAgent
        - Update daily macros
        - Update memory patterns
        - Return daily status
        """
        user_agent = self.agents.get("user")
        memory_agent = self.agents.get("memory")

        # Log meal
        result = {"success": False}
        if user_agent:
            logged = await user_agent.process({
                "action": "log_meal",
                "user_id": user_id,
                "meal_data": meal_data
            })
            result["meal_logged"] = logged
            result["daily_status"] = await user_agent.process({
                "action": "get_daily_macros",
                "user_id": user_id,
                "date": meal_data.get("date")
            })
            result["success"] = True

            # Update memory
            if memory_agent:
                await memory_agent.process({
                    "action": "record_meal",
                    "user_id": user_id,
                    "meal_data": meal_data
                })

        return result

    async def workflow_recipe_suggestions(self, user_id: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recipe suggestions through RecipeAgent.
        Optionally filter by user preferences.
        """
        # Get user preferences
        user_agent = self.agents.get("user")
        prefs = {}
        if user_agent:
            prefs = await user_agent.process({"action": "get_preferences", "user_id": user_id})

        # Merge constraints with preferences
        merged = {**constraints, **prefs}

        # Use meal planner to get suggestions (or recipe agent directly)
        meal_planner = self.agents.get("meal_planner")
        if meal_planner:
            return await meal_planner.process({
                "action": "suggest_meals",
                "user_id": user_id,
                **merged
            })
        return {"suggestions": []}

    async def workflow_get_recommendations(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Wrap RecommendationAgent."""
        rec_agent = self.agents.get("recommendation")
        if rec_agent:
            return await rec_agent.process({
                "action": "generate",
                "user_id": user_id,
                "days": days
            })
        return {"error": "Recommendation agent not available"}

    async def _handle_direct_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        For direct agent access (e.g., specific API endpoint routes).
        Expects {'agent': str, 'action': str, ...}
        """
        agent_name = request.get("agent")
        if not agent_name:
            raise ValueError("Agent name required for direct action")
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")
        # Remove orchestration-specific keys and pass rest to agent
        clean_req = {k: v for k, v in request.items() if k not in ("action", "agent")}
        return await agent.process(clean_req)

    async def health(self) -> Dict[str, Any]:
        """Health of orchestrator and all agents."""
        status = {
            "orchestrator": "healthy",
            "agents": {}
        }
        for name, agent in self.agents.items():
            try:
                h = await agent.health()
                status["agents"][name] = h["status"]
            except Exception as e:
                status["agents"][name] = f"error: {str(e)}"
        return status
