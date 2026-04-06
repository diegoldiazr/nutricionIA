"""
API Routes Package - Centralized API endpoints.

All routes delegate to the OrchestratorAgent for business logic.
"""
from .routes import router as api_router

__all__ = ["api_router"]
