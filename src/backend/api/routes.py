"""
API Routes - All endpoints delegate to OrchestratorAgent.

This module contains all HTTP endpoints for the nutrition assistant.
Business logic is handled by the orchestrator which coordinates agents.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import Dict, Any, Optional
from datetime import datetime

from .dependencies import get_orchestrator, get_db_service
from agents.orchestrator_agent.agent import OrchestratorAgent
from database.service import DatabaseService

router = APIRouter(prefix="/api/v1", tags=["orchestrator"])


# =============================================================================
# Profile Endpoints
# =============================================================================

@router.post("/profile")
async def create_profile(
    profile_data: Dict[str, Any] = Body(...),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Create a new user profile.

    Expected body:
    {
        "email": "user@example.com",
        "name": "John Doe",
        "age": 30,
        "gender": "male",
        "height": 175,
        "weight_current": 80,
        "activity_level": "moderate",
        "goal": "lose_weight"
    }
    """
    try:
        result = await orchestrator.process({
            "action": "create_profile",
            "agent": "user",
            "user_data": profile_data
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: int,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """Get user profile by ID."""
    try:
        result = await orchestrator.process({
            "agent": "user",
            "action": "get_profile",
            "user_id": user_id
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile/{user_id}")
async def update_profile(
    user_id: int,
    updates: Dict[str, Any] = Body(...),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """Update user profile fields."""
    try:
        result = await orchestrator.process({
            "agent": "user",
            "action": "update_profile",
            "user_id": user_id,
            "updates": updates
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Meal Endpoints
# =============================================================================

@router.post("/log-meal")
async def log_meal(
    meal_data: Dict[str, Any] = Body(...),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Log a meal for a user.

    Expected body:
    {
        "user_id": 1,
        "date": "2025-04-06",
        "meal_type": "lunch",
        "food_items": [
            {"name": "chicken breast", "quantity": 150, "unit": "g",
             "calories": 250, "protein": 45, "carbs": 0, "fat": 6}
        ],
        "notes": "Optional notes"
    }
    """
    try:
        result = await orchestrator.process({
            "action": "log_meal",
            "user_id": meal_data["user_id"],
            "meal_data": meal_data
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-summary/{user_id}")
async def get_daily_summary(
    user_id: int,
    date_str: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get daily summary: profile, macros consumed, targets, meal suggestions.

    Returns:
    {
        "user_id": 1,
        "date": "2025-04-06",
        "profile": {...},
        "daily_macros": {"calories": 1200, "protein": 90, ...},
        "nutrition_status": {
            "targets": {...},
            "remaining": {"calories": 700, "protein": 70, ...}
        },
        "meal_suggestions": [...]
    }
    """
    try:
        result = await orchestrator.process({
            "action": "daily_summary",
            "user_id": user_id,
            "date": date_str
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meal-suggestions/{user_id}")
async def get_meal_suggestions(
    user_id: int,
    meal_type: str = Query("lunch", description="Meal type: breakfast, lunch, dinner, snack"),
    remaining_calories: Optional[int] = Query(None, description="Remaining calories to target"),
    remaining_protein: Optional[int] = Query(None, description="Remaining protein (g)"),
    remaining_carbs: Optional[int] = Query(None, description="Remaining carbs (g)"),
    remaining_fat: Optional[int] = Query(None, description="Remaining fat (g)"),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get meal suggestions based on remaining macros and preferences.
    """
    try:
        remaining = {}
        if remaining_calories is not None:
            remaining["calories"] = remaining_calories
        if remaining_protein is not None:
            remaining["protein"] = remaining_protein
        if remaining_carbs is not None:
            remaining["carbs"] = remaining_carbs
        if remaining_fat is not None:
            remaining["fat"] = remaining_fat

        result = await orchestrator.process({
            "action": "recipe_suggestions",
            "user_id": user_id,
            "constraints": {
                "meal_type": meal_type,
                "remaining_macros": remaining
            }
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Progress Endpoints
# =============================================================================

@router.get("/progress-analysis/{user_id}")
async def get_progress_analysis(
    user_id: int,
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Get weekly progress analysis.

    Returns:
    {
        "overall_score": float,
        "weight_trend": {...},
        "calorie_adherence": {...},
        "summary": {...}
    }
    """
    try:
        result = await orchestrator.process({
            "action": "progress_report",
            "user_id": user_id,
            "days": days
        })
        return result.get("progress_analysis", result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{user_id}")
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
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Settings Endpoints
# =============================================================================

@router.post("/settings/{user_id}")
async def update_settings(
    user_id: int,
    settings: Dict[str, Any] = Body(...),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Update user settings and preferences.

    Expected body:
    {
        "dietary_restrictions": ["gluten-free"],
        "favorite_foods": [...],
        "disliked_foods": [...],
        "cooking_equipment": ["airfryer", "oven"],
        "prep_time_max": 45,
        "difficulty_max": "medium"
    }
    """
    try:
        result = await orchestrator.process({
            "agent": "user",
            "action": "set_preferences",
            "user_id": user_id,
            "preferences": settings
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/{user_id}")
async def get_settings(
    user_id: int,
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """Get user preferences and settings."""
    try:
        result = await orchestrator.process({
            "agent": "user",
            "action": "get_preferences",
            "user_id": user_id
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Knowledge Endpoints
# =============================================================================

@router.get("/knowledge/query")
async def query_knowledge(
    query: str = Query(..., description="Nutrition question to query NotebookLM"),
    orchestrator: OrchestratorAgent = Depends(get_orchestrator)
):
    """
    Query the knowledge base (NotebookLM) for grounded nutrition information.

    This endpoint NEVER fabricates nutritional facts - all responses come
    directly from NotebookLM retrieval.
    """
    try:
        result = await orchestrator.process({
            "agent": "knowledge",
            "query": query
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
