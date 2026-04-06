"""
Orchestrator Agent - Coordinates agent communication without circular dependencies.
"""

from typing import Dict, Any
from ..base_agent import BaseAgent
from core.exceptions import AgentError


class OrchestratorAgent(BaseAgent):
    """
    Central controller for agent system.
    """

    def __init__(
        self,
        agent_id: str = "orchestrator",
        agents: Dict[str, BaseAgent] = None,
        event_bus=None,
        **kwargs
    ):
        super().__init__(agent_id=agent_id, name="Orchestrator Agent", event_bus=event_bus)
        self.agents = agents or {}
        for agent in self.agents.values():
            if hasattr(agent, 'orchestrator'):
                agent.orchestrator = self

    async def initialize(self) -> None:
        await super().initialize()
        for agent in self.agents.values():
            await agent.initialize()

    async def shutdown(self) -> None:
        for agent in self.agents.values():
            await agent.shutdown()
        await super().shutdown()

    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        action = request.get("action", "")
        if not action:
            raise AgentError("Action is required")

        handlers = {
            "daily_summary": lambda: self.workflow_daily_summary(request["user_id"], request.get("date")),
            "progress_report": lambda: self.workflow_progress_report(request["user_id"], request.get("days", 7)),
            "log_meal": lambda: self.workflow_log_meal(request["user_id"], request["meal_data"]),
            "recipe_suggestions": lambda: self.workflow_recipe_suggestions(request["user_id"], request.get("constraints", {})),
            "get_recommendations": lambda: self.workflow_get_recommendations(request["user_id"], request.get("days", 7)),
        }

        if action not in handlers:
            return await self._handle_direct_action(request)

        return await handlers[action]()

    async def workflow_daily_summary(self, user_id: int, date_str: str = None) -> Dict[str, Any]:
        """Generate combined daily summary."""
        summary = {
            "user_id": user_id, "date": date_str, "profile": None,
            "daily_macros": None, "nutrition_status": {}, "meal_suggestions": [],
        }
        user_agent = self.agents.get("user")
        nutrition = self.agents.get("nutrition")
        meal_planner = self.agents.get("meal_planner")

        if not user_agent:
            raise AgentError("User agent not available")

        try:
            profile = await user_agent.process({"action": "get_profile", "user_id": user_id})
            summary["profile"] = profile
            macros_resp = await user_agent.process({"action": "get_daily_macros", "user_id": user_id, "date": date_str})
            summary["daily_macros"] = macros_resp
        except Exception:
            pass

        if summary["profile"] and nutrition:
            try:
                targets = await nutrition.process({"action": "calculate_targets", "profile": summary["profile"]})
                summary["nutrition_status"]["targets"] = targets
                consumed = summary["daily_macros"] or {}
                remaining = {
                    "calories": max(0, targets["daily_calories"] - consumed.get("calories", 0)),
                    "protein": max(0, targets["macro_breakdown"]["protein_grams"] - consumed.get("protein", 0)),
                    "carbs": max(0, targets["macro_breakdown"]["carbs_grams"] - consumed.get("carbs", 0)),
                    "fat": max(0, targets["macro_breakdown"]["fat_grams"] - consumed.get("fat", 0)),
                }
                summary["nutrition_status"]["remaining"] = remaining
                if remaining["calories"] > 100 and meal_planner:
                    suggestions = await meal_planner.process({
                        "action": "suggest_meals", "user_id": user_id,
                        "remaining_calories": remaining["calories"],
                        "remaining_macros": remaining, "meal_type": "dinner"
                    })
                    summary["meal_suggestions"] = suggestions.get("suggestions", [])
            except Exception:
                pass

        return summary

    async def workflow_log_meal(self, user_id: int, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        user_agent = self.agents.get("user")
        if not user_agent:
            raise AgentError("User agent not available")
        result = await user_agent.process({"action": "log_meal", "user_id": user_id, "meal_data": meal_data})
        return {"success": True, "meal_logged": result}

    async def workflow_recipe_suggestions(self, user_id: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        user_agent = self.agents.get("user")
        meal_planner = self.agents.get("meal_planner")
        if not meal_planner:
            return {"suggestions": []}
        prefs = {}
        if user_agent:
            try:
                prefs = await user_agent.process({"action": "get_preferences", "user_id": user_id})
            except:
                pass
        merged = {**constraints, **prefs}
        return await meal_planner.process({"action": "suggest_meals", "user_id": user_id, **merged})

    async def workflow_progress_report(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        progress = self.agents.get("progress")
        if progress:
            return await progress.process({"action": "analyze", "user_id": user_id, "days": days})
        return {"error": "Progress agent not available"}

    async def workflow_get_recommendations(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        rec = self.agents.get("recommendation")
        if rec:
            return await rec.process({"action": "generate", "user_id": user_id, "days": days})
        return {"error": "Recommendation agent not available"}

    async def _handle_direct_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = request.get("agent")
        if not agent_name:
            raise AgentError("Agent name required")
        agent = self.agents.get(agent_name)
        if not agent:
            raise AgentError(f"Agent '{agent_name}' not found")
        clean_req = {k: v for k, v in request.items() if k not in ("action", "agent")}
        return await agent.process(clean_req)

    async def health(self) -> Dict[str, Any]:
        status = {"orchestrator": "healthy", "agents": {}}
        for name, agent in self.agents.items():
            try:
                h = await agent.health()
                status["agents"][name] = h.get("status", "unknown")
            except Exception as e:
                status["agents"][name] = f"error: {str(e)}"
        return status
