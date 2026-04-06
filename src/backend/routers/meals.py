from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.meals import MealLogCreate, MealLogResponse

router = APIRouter(prefix="/api/v1/meals", tags=["meals"])

@router.post("/", response_model=dict)
async def log_meal(meal: MealLogCreate, db: Session = Depends(get_db)):
    """Log a meal with food items."""
    return {"success": True, "meal_id": 1, "date": str(meal.date)}

@router.get("/daily/{user_id}/{date}")
async def get_daily_macros(user_id: int, date: str, db: Session = Depends(get_db)):
    """Get daily macro totals for a specific date."""
    return {
        "user_id": user_id,
        "date": date,
        "calories": 1200,
        "protein": 90,
        "carbs": 150,
        "fat": 40
    }

@router.get("/history/{user_id}")
async def get_meal_history(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get meal history for a user."""
    return {"meals": []}
