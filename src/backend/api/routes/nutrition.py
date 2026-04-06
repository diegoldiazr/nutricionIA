"""
Nutrition calculation endpoints.
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="", tags=["nutrition"])

@router.get("/nutrition/targets/{user_id}", response_model=Dict[str, Any])
async def get_nutrition_targets(user_id: int) -> Dict[str, Any]:
    return {
        "user_id": user_id,
        "daily_calories": 2000,
        "macro_breakdown": {
            "protein_grams": 120,
            "carbs_grams": 250,
            "fat_grams": 67,
        }
    }

@router.get("/nutrition/remaining/{user_id}", response_model=Dict[str, Any])
async def get_remaining_nutrition(
    user_id: int,
    date: str = None
) -> Dict[str, Any]:
    return {
        "user_id": user_id,
        "date": date,
        "remaining": {
            "calories": 1200,
            "protein": 60,
            "carbs": 80,
            "fat": 30,
        }
    }
