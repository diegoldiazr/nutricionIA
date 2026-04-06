"""
User Agent - Manages user data: profile, preferences, weight history, meal logs.
"""
from datetime import datetime, date
from typing import Dict, Any, Optional, List

class UserAgent:
    """
    Manages all user-specific data:
    - Profile (age, gender, height, weight, goals)
    - Preferences (dietary restrictions, equipment)
    - Weight history
    - Meal logging
    """
    
    def __init__(self, database):
        """
        Initialize UserAgent with database session.
        
        Args:
            database: Database service (SQLAlchemy session or service)
        """
        self.db = database
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile."""
        # Implementation would create in DB
        return {'id': 1, **user_data, 'created_at': datetime.utcnow()}
    
    async def get_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile."""
        # Demo data - in real version fetch from DB
        return {
            'id': user_id,
            'name': 'Demo User',
            'email': 'user@example.com',
            'age': 30,
            'gender': 'male',
            'height': 175.0,
            'weight_current': 80.0,
            'activity_level': 'moderate',
            'goal': 'lose_weight',
            'created_at': datetime.utcnow()
        }
    
    async def update_profile(self, user_id: int, updates: Dict[str, Any]) -> bool:
        """Update user profile."""
        # Would update DB
        return True
    
    async def get_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences."""
        return {
            'user_id': user_id,
            'dietary_restrictions': [],
            'favorite_foods': ['chicken breast', 'brown rice', 'broccoli'],
            'disliked_foods': ['shellfish', 'olives'],
            'cooking_equipment': ['airfryer', 'stove', 'oven'],
            'prep_time_max': 45,
            'difficulty_max': 'medium'
        }
    
    async def log_meal(self, user_id: int, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log a meal entry."""
        return {
            'id': 1,
            'user_id': user_id,
            'date': meal_data.get('date', date.today().isoformat()),
            'meal_type': meal_data.get('meal_type', 'lunch'),
            'food_items': meal_data.get('food_items', []),
            'notes': meal_data.get('notes'),
            'created_at': datetime.utcnow()
        }
    
    async def get_daily_macros(self, user_id: int, target_date: str) -> Optional[Dict[str, int]]:
        """
        Get aggregated macros for a specific date.
        
        Returns:
            Dict with calories, protein, carbs, fat totals
        """
        # In real implementation, query database and sum food items from meals table
        return {
            'calories': 1200,
            'protein': 90,
            'carbs': 150,
            'fat': 40
        }
    
    async def get_weight_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get weight history for analysis."""
        # Demo data
        return [
            {'date': '2025-04-01', 'weight': 82.5},
            {'date': '2025-04-02', 'weight': 82.3},
            {'date': '2025-04-03', 'weight': 82.1},
        ]
    
    async def update_weight(self, user_id: int, weight: float, date: str = None) -> bool:
        """Add weight entry to history."""
        # Would insert into weight_history table
        return True
