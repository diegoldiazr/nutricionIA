"""
Main FastAPI Application Entry Point - Refactored Version

Uses:
- Agent factory for dependency injection
- Event bus for decoupled communication
- Repository pattern for data access
- Clean separation of concerns
"""

import os
import sys
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import text

# Configure path for relative imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core imports
from core.events import event_bus, EventType, Event
from core.logging import setup_logging, get_logger
from core.exceptions import NutritionAppError

# Configuration
from config.settings import settings

# Database
from database.service import DatabaseService
from database.models import Base

# Repositories
from database.repositories.user_repository import UserRepository
from database.repositories.macro_repository import MacroRepository
from database.repositories.preference_repository import PreferenceRepository
from database.repositories.memory_repository import MemoryRepository

# Agents
from agents.base_agent import BaseAgent
from agents.knowledge_agent.agent import KnowledgeAgent
from agents.user_agent.agent import UserAgent
from agents.nutrition_agent.agent import NutritionAgent
from agents.meal_planner_agent.agent import MealPlannerAgent
from agents.recipe_agent.agent import RecipeAgent
from agents.progress_agent.agent import ProgressAgent
from agents.recommendation_agent.agent import RecommendationAgent
from agents.memory_agent.agent import MemoryAgent
from agents.orchestrator_agent.agent import OrchestratorAgent

# Services
from services.openrouter_service import OpenRouterService, OpenRouterConfig
from services.notebooklm_service import NotebookLMService

# Configure logging
setup_logging(level="DEBUG")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle - handles startup and shutdown.
    """
    print("Initializing Nutrition Assistant API...")

    # 1. Initialize database
    print("  - Initializing database...")
    db_service = DatabaseService(settings.database_url)
    await db_service.init_db()
    app.state.db_service = db_service
    print("  - Database initialized.")

    # 2. Create database repositories
    print("  - Creating repositories...")
    session = db_service.SessionLocal()
    repositories = {
        'users': UserRepository(session),
        'macros': MacroRepository(session),
        'preferences': PreferenceRepository(session),
        'memory': MemoryRepository(session),
    }
    app.state.repositories = repositories
    print("  - Repositories created.")

    # 3. Initialize services
    print("  - Initializing services...")
    notebooklm = NotebookLMService(
        api_url=settings.NOTEBOOKLM.api_url,
        notion_token=settings.NOTION.token,
        timeout=settings.NOTEBOOKLM.timeout,
        max_retries=settings.NOTEBOOKLM.max_retries
    )
    openrouter = OpenRouterService(config=OpenRouterConfig(
        api_key=settings.OPENROUTER.api_key,
        default_model=settings.OPENROUTER.model,
        site_url=settings.OPENROUTER.site_url,
        site_name=settings.OPENROUTER.site_name,
        timeout=settings.OPENROUTER.timeout,
        max_retries=settings.OPENROUTER.max_retries
    ))
    print("  - Services initialized.")

    # 4. Create agents with proper dependencies
    print("  - Creating agents...")

    knowledge_agent = KnowledgeAgent(
        agent_id="knowledge",
        notebooklm_service=notebooklm,
        event_bus=event_bus
    )

    user_agent = UserAgent(
        agent_id="user",
        repositories=repositories,
        event_bus=event_bus
    )

    nutrition_agent = NutritionAgent(
        agent_id="nutrition",
        openrouter_service=openrouter,
        event_bus=event_bus
    )

    recipe_agent = RecipeAgent(
        agent_id="recipe",
        knowledge_agent=knowledge_agent,
        event_bus=event_bus
    )

    meal_planner_agent = MealPlannerAgent(
        agent_id="meal_planner",
        knowledge_agent=knowledge_agent,
        event_bus=event_bus
    )

    progress_agent = ProgressAgent(
        agent_id="progress",
        user_agent=user_agent,
        nutrition_agent=nutrition_agent,
        event_bus=event_bus
    )

    memory_agent = MemoryAgent(
        agent_id="memory",
        repositories=repositories,
        event_bus=event_bus
    )

    recommendation_agent = RecommendationAgent(
        agent_id="recommendation",
        nutrition_agent=nutrition_agent,
        progress_agent=progress_agent,
        user_agent=user_agent,
        memory_agent=memory_agent,
        event_bus=event_bus
    )

    orchestrator = OrchestratorAgent(
        agents={
            'knowledge': knowledge_agent,
            'user': user_agent,
            'nutrition': nutrition_agent,
            'meal_planner': meal_planner_agent,
            'recipe': recipe_agent,
            'progress': progress_agent,
            'recommendation': recommendation_agent,
            'memory': memory_agent,
        },
        event_bus=event_bus
    )

    # Store references
    app.state.knowledge_agent = knowledge_agent
    app.state.user_agent = user_agent
    app.state.nutrition_agent = nutrition_agent
    app.state.meal_planner_agent = meal_planner_agent
    app.state.recipe_agent = recipe_agent
    app.state.progress_agent = progress_agent
    app.state.recommendation_agent = recommendation_agent
    app.state.memory_agent = memory_agent
    app.state.orchestrator = orchestrator

    # Initialize all agents
    await orchestrator.initialize()
    print("All agents initialized and ready.")

    yield

    # Shutdown
    print("Shutting down API...")
    await orchestrator.shutdown()
    await notebooklm.close()
    await openrouter.close()
    print("Shutdown complete.")


# Create app
app = FastAPI(
    title=settings.app_name,
    description="Multi-agent AI Nutrition Assistant",
    version=settings.app_version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
from api import api_router
app.include_router(api_router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Nutrition Assistant API",
        "status": "running",
        "version": settings.app_version
    }


@app.get("/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "healthy"}


@app.get("/health/agents")
async def agents_health_check():
    """Health status of all agents."""
    health_data = {}
    for name in ['knowledge', 'user', 'nutrition', 'meal_planner', 
                 'recipe', 'progress', 'recommendation', 'memory', 'orchestrator']:
        agent = getattr(app.state, f"{name}_agent", None)
        if agent and hasattr(agent, 'health'):
            try:
                health_data[name] = await agent.health()
            except Exception as e:
                health_data[name] = {"status": f"error: {str(e)}"}
        elif name == 'orchestrator':
            agent = getattr(app.state, 'orchestrator', None)
            if agent:
                try:
                    health_data[name] = await agent.health()
                except Exception as e:
                    health_data[name] = {"status": f"error: {str(e)}"}
        else:
            health_data[name] = {"status": "not found"}

    return health_data


# Error handler
@app.exception_handler(NutritionAppError)
async def nutrition_error_handler(request: Request, exc: NutritionAppError):
    logger.error(f"Application error: {exc}")
    return {"error": str(exc), "type": type(exc).__name__}, 500


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
