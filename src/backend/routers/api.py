"""
Main API Router - Endpoints that call the Orchestrator Agent.
All business logic routes through the orchestrator.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from typing import Dict, Any, Optional
from datetime import date, datetime
from ...services import DatabaseService
from ...agents import OrchestrationAgent

router = APIRouter(prefix="/api/v1", tags=["orchestrator"])

# Dependencies to get agents from app state
def get_orchestrator(request) -> OrchestrationAgent:
    return request.app.state.orchestrator

def get_db_service(request) -> DatabaseService:
    return request.app.state.db_service

@router.post("/profile")
async def create_profile(
    profile_data: Dict[str, Any] = Body(...),
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
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
        # Delegate to user agent via orchestrator
        result = await orchestrator.process({
            "action": "get_profile",  # Will be expanded
            "agent": "user",
            "request": {"action": "create_profile", "user_data": profile_data}
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: int,
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
):
    """Get user profile."""
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
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
):
    """Update user profile."""
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


@router.post("/log-meal")
async def log_meal(
    meal_data: Dict[str, Any] = Body(...),
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
):
    """
    Log a meal.

    Expected body:
    {
        "user_id": 1,
        "date": "2025-04-06",
        "meal_type": "lunch",
        "food_items": [
            {"name": "chicken breast", "quantity": 150, "unit": "g", "calories": 250, "protein": 45, "carbs": 0, "fat": 6}
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
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
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
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
):
    """
    Get meal suggestions for user based on remaining macros and preferences.

    Can optionally pass remaining macros as query parameters.
    If not provided, will fetch from daily summary context.
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


@router.get("/progress-analysis/{user_id}")
async def get_progress_analysis(
    user_id: int,
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
):
    """
    Get weekly progress analysis.

    Returns:
    {
        "weight_change_weekly": float,
        "weight_trend": "stable",
        "avg_daily_calories": float,
        "avg_protein_per_kg": float,
        "adherence_rate": float,
        "training_days": int,
        "hunger_patterns": {...}
    }
    """
    try:
        result = await orchestrator.process({
            "action": "progress_report",
            "user_id": user_id,
            "days": days
        })
        return result.get("progress_analysis", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/{user_id}")
async def get_dashboard(
    user_id: int,
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
):
    """
    Get complete dashboard data: summary, recommendations, progress.

    Combines:
    - Daily summary
    - Progress analysis
    - Recommendations
    """
    try:
        # Get daily summary
        summary = await orchestrator.process({
            "action": "daily_summary",
            "user_id": user_id
        })

        # Get progress report
        report = await orchestrator.process({
            "action": "progress_report",
            "user_id": user_id,
            "days": 7
        })

        return {
            "daily_summary": summary,
            "progress_report": report,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/{user_id}")
async def update_settings(
    user_id: int,
    settings: Dict[str, Any] = Body(...),
    orchestrator: OrchestrationAgent = Depends(get_orchestrator)
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
