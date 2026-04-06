"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from core.events import event_bus

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(
    orchestrator=None
) -> Dict[str, Any]:
    """Simple health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@router.get("/agents")
async def agents_health(
    orchestrator=None
) -> Dict[str, Any]:
    """Health status of all agents."""
    if orchestrator:
        return await orchestrator.health()
    else:
        # Without orchestrator, return basic health
        return {
            "orchestrator": "unavailable",
            "agents": {},
            "status": "degraded"
        }
