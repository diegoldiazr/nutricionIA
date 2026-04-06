"""
SQLAlchemy ORM Models for Nutrition AI Assistant.

Tables:
- users: User profiles with physiological data
- weight_history: Weight tracking over time
- daily_macros: Daily macronutrient consumption
- preferences: User dietary preferences
- memory_patterns: Learned patterns for personalization
"""
from sqlalchemy import Column, Integer, String, Float, Date, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    User profile table.

    Stores physiological data and goals for nutrition calculations.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # "male" | "female" | "other"
    height = Column(Float, nullable=False)  # cm
    weight_current = Column(Float, nullable=False)  # kg
    activity_level = Column(String, nullable=False)  # sedentary, light, moderate, active, very_active
    goal = Column(String, nullable=False)  # lose_weight, maintain, gain_muscle
    profile_data = Column(JSON, default=dict)  # Additional flexible data

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    weight_history = relationship("WeightHistory", back_populates="user", cascade="all, delete-orphan")
    daily_macros = relationship("DailyMacro", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("Preference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    memory_patterns = relationship("MemoryPattern", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class WeightHistory(Base):
    """
    Weight tracking history.

    Records user weight over time for progress analysis.
    """
    __tablename__ = "weight_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)
    weight = Column(Float, nullable=False)  # kg
    notes = Column(String, default="")  # Optional notes (e.g., "morning weigh-in")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="weight_history")

    def __repr__(self) -> str:
        return f"<WeightHistory(user_id={self.user_id}, date={self.date}, weight={self.weight}kg)>"


class DailyMacro(Base):
    """
    Daily macronutrient consumption tracker.

    Records calories and macros consumed each day.
    """
    __tablename__ = "daily_macros"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, default=datetime.utcnow)

    # Consumed macros
    calories = Column(Integer, default=0)
    carbs = Column(Integer, default=0)  # grams
    protein = Column(Integer, default=0)  # grams
    fat = Column(Integer, default=0)  # grams

    # Meal breakdown (optional detailed tracking)
    meals = Column(JSON, default=list)  # List of meal entries

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="daily_macros")

    def __repr__(self) -> str:
        return f"<DailyMacro(user_id={self.user_id}, date={self.date}, calories={self.calories})>"


class Preference(Base):
    """
    User dietary preferences and constraints.

    Used for meal planning and recipe suggestions.
    """
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Dietary restrictions
    dietary_restrictions = Column(JSON, default=list)  # e.g., ["vegetarian", "gluten-free"]
    allergies = Column(JSON, default=list)  # e.g., ["peanuts", "shellfish"]

    # Food preferences
    favorite_foods = Column(JSON, default=list)  # Favorite ingredients/meals
    disliked_foods = Column(JSON, default=list)  # Foods to avoid

    # Cooking constraints
    cooking_equipment = Column(JSON, default=list)  # e.g., ["airfryer", "thermomix", "oven"]
    prep_time_max = Column(Integer, default=45)  # Maximum prep time in minutes
    difficulty_max = Column(String, default="medium")  # easy, medium, hard

    # Meal timing
    meals_per_day = Column(Integer, default=3)
    snack_preference = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self) -> str:
        return f"<Preference(user_id={self.user_id}, restrictions={self.dietary_restrictions})>"


class MemoryPattern(Base):
    """
    User behavior patterns for personalization.

    Automatically updated based on user activity to enable
    smarter recommendations over time.
    """
    __tablename__ = "memory_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # Learned patterns
    favorite_meals = Column(JSON, default=list)  # Frequently logged meals
    recurring_foods = Column(JSON, default=list)  # Common ingredients
    hunger_patterns = Column(JSON, default=dict)  # e.g., {"afternoon_slump": true}
    meal_timing_preferences = Column(JSON, default=dict)  # Preferred meal times

    # Behavioral insights
    adherence_score = Column(Float, default=0.0)  # 0-1 adherence tracking
    favorite_cuisines = Column(JSON, default=list)
    avoided_ingredients = Column(JSON, default=list)

    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="memory_patterns")

    def __repr__(self) -> str:
        return f"<MemoryPattern(user_id={self.user_id}, favorite_meals={len(self.favorite_meals)})>"
