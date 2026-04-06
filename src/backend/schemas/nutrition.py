from pydantic import BaseModel
from typing import Dict, Any

class BMRResponse(BaseModel):
    bmr: float
    tdee: float
    activity_multiplier: float
    calculation_method: str

class MacroBreakdown(BaseModel):
    calories: int
    protein: int  # grams
    carbs: int    # grams
    fat: int      # grams
    protein_percentage: float
    carbs_percentage: float
    fat_percentage: float

class NutritionTargets(BaseModel):
    daily_calories: int
    macro_breakdown: MacroBreakdown
    weight_change_rate: float  # kg per week
    protein_target: int  # grams
    rationale: Optional[Dict[str, Any]] = None
