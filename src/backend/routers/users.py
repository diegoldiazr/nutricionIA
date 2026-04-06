from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..database.models import User
from ..schemas.user import UserCreate, UserResponse, UserUpdate
from typing import Optional

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user profile."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create user in DB
    return {"id": 1, **user.model_dump(), "created_at": "2025-04-01T00:00:00"}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user profile by ID."""
    return {"id": user_id, "name": "Demo", "email": "demo@example.com", "age": 30, "gender": "male", "height": 175, "weight_current": 80, "activity_level": "moderate", "goal": "lose_weight", "created_at": "2025-04-01T00:00:00"}

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, updates: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile."""
    return {"id": user_id, **updates.model_dump(exclude_unset=True)}

@router.post("/{user_id}/weight")
async def log_weight(user_id: int, weight_data: dict, db: Session = Depends(get_db)):
    """Log a weight entry."""
    return {"success": True, "user_id": user_id, "weight": weight_data.get("weight")}
