from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List, Dict, Any

class UserBase(BaseModel):
    email: EmailStr
    name: str
    age: int
    gender: str  # male, female, other
    height: float  # cm
    weight_current: float  # kg
    activity_level: str  # sedentary, light, moderate, active, very_active
    goal: str  # lose_weight, maintain, gain_muscle

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight_current: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class WeightHistoryResponse(BaseModel):
    id: int
    user_id: int
    date: date
    weight: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class PreferenceResponse(BaseModel):
    id: int
    user_id: int
    dietary_restrictions: List[str] = []
    favorite_foods: List[str] = []
    disliked_foods: List[str] = []
    cooking_equipment: List[str] = []
    prep_time_max: Optional[int] = None
    difficulty_max: Optional[str] = None
    
    class Config:
        from_attributes = True
