from sqlalchemy import Column, Integer, String, Float, Date, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from . import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    height = Column(Float)
    weight_current = Column(Float)
    activity_level = Column(String)
    goal = Column(String)
    profile_data = Column(JSON)  # Additional flexible data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    weight_history = relationship("WeightHistory", back_populates="user")
    daily_macros = relationship("DailyMacro", back_populates="user")
    preferences = relationship("Preference", back_populates="user", uselist=False)

class WeightHistory(Base):
    __tablename__ = "weight_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    weight = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="weight_history")

class DailyMacro(Base):
    __tablename__ = "daily_macros"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    calories = Column(Integer)
    carbs = Column(Integer)
    protein = Column(Integer)
    fat = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="daily_macros")

class Preference(Base):
    __tablename__ = "preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    dietary_restrictions = Column(JSON, default=list)
    favorite_foods = Column(JSON, default=list)
    disliked_foods = Column(JSON, default=list)
    cooking_equipment = Column(JSON, default=list)  # airfryer, thermomix, etc.
    prep_time_max = Column(Integer)  # minutes
    difficulty_max = Column(String)  # easy, medium, hard
    
    user = relationship("User", back_populates="preferences")

class MemoryPattern(Base):
    __tablename__ = "memory_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    favorite_meals = Column(JSON, default=list)
    recurring_foods = Column(JSON, default=list)
    hunger_patterns = Column(JSON, default=dict)
    meal_timing_preferences = Column(JSON, default=dict)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
