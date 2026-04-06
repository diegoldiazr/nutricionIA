"""
Profile management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="", tags=["profiles"])

class ProfileCreate(BaseModel):
    email: EmailStr
    name: str
    age: int
    gender: str
    height: float
    weight_current: float
    activity_level: str
    goal: str
    profile_data: Dict[str, Any] = {}

class ProfileUpdate(BaseModel):
    name: str = None
    age: int = None
    weight_current: float = None
    activity_level: str = None
    goal: str = None
    profile_data: Dict[str, Any] = None

@router.post("/profiles", response_model=Dict[str, Any])
async def create_profile(profile: ProfileCreate) -> Dict[str, Any]:
    return {"id": 1, "email": profile.email, "name": profile.name}

@router.get("/profiles/{user_id}", response_model=Dict[str, Any])
async def get_profile(user_id: int) -> Dict[str, Any]:
    return {"id": user_id, "email": "user@example.com"}

@router.put("/profiles/{user_id}", response_model=Dict[str, Any])
async def update_profile(user_id: int, profile: ProfileUpdate) -> Dict[str, Any]:
    return {"id": user_id, "updated": True}
