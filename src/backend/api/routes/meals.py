"""
Meal logging endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["meals"])

class MealLog(BaseModel):
    date: str
    macros: Dict[str, int]
    description: str = ""

@router.post("/log-meal", response_model=Dict[str, Any])
async def log_meal(user_id: int, meal: MealLog) -> Dict[str, Any]:
    return {"success": True, "user_id": user_id, "date": meal.date}

@router.post("/meals/log", response_model=Dict[str, Any])
async def log_meal_alt(user_id: int, meal: MealLog) -> Dict[str, Any]:
    return {"success": True, "user_id": user_id, "date": meal.date}
