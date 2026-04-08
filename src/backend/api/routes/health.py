"""
Health check endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from typing import Dict, Any
from core.events import event_bus

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> Dict[str, Any]:
    """Simple health check."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
