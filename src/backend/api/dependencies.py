"""
FastAPI Dependencies - Clean dependency injection for API routes.
"""
from fastapi import Request
from agents.orchestrator_agent.agent import OrchestratorAgent
from database.service import DatabaseService


def get_orchestrator(request: Request) -> OrchestratorAgent:
    """Get OrchestratorAgent from app state."""
    return request.app.state.orchestrator


def get_db_service(request: Request) -> DatabaseService:
    """Get DatabaseService from app state."""
    return request.app.state.db_service
