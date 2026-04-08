"""
Dashboard API Route - Combined dashboard data.
"""
from fastapi import APIRouter, Depends
from datetime import datetime
from ..dependencies import get_orchestrator
from agents.orchestrator_agent.agent import OrchestratorAgent

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{user_id}")
async def get_dashboard(
    user_id: int,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get complete dashboard data combining daily summary, progress, and recommendations.
    """
    try:
        summary = await orchestrator.process({
            "action": "daily_summary",
            "user_id": user_id
        })

        report = await orchestrator.process({
            "action": "progress_report",
            "user_id": user_id,
            "days": 7
        })

        recommendations = await orchestrator.process({
            "action": "get_recommendations",
            "user_id": user_id,
            "days": 7
        })

        return {
            "daily_summary": summary,
            "progress_report": report,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}
