from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class MealLogCreate(BaseModel):
    user_id: int
    date: date
    meal_type: str  # breakfast, lunch, dinner, snack
    food_items: List[Dict[str, Any]]  # [{name: str, quantity: float, unit: str, calories: int, protein: float, carbs: float, fat: float}]
    notes: Optional[str] = None

class MealLogResponse(BaseModel):
    id: int
    user_id: int
    date: date
    meal_type: str
    food_items: List[Dict[str, Any]]
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
