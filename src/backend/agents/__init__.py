"""Agents package."""
__all__ = [
    'BaseAgent',
    'AgentFactory',
    'create_agent_factory',
]

from .base_agent import BaseAgent
from .factory import AgentFactory, create_agent_factory

from .knowledge_agent.agent import KnowledgeAgent
from .user_agent.agent import UserAgent
from .nutrition_agent.agent import NutritionAgent
from .meal_planner_agent.agent import MealPlannerAgent
from .recipe_agent.agent import RecipeAgent
from .progress_agent.agent import ProgressAgent
from .recommendation_agent.agent import RecommendationAgent
from .memory_agent.agent import MemoryAgent
from .orchestrator_agent.agent import OrchestratorAgent

__all__.extend([
    'KnowledgeAgent', 'UserAgent', 'NutritionAgent',
    'MealPlannerAgent', 'RecipeAgent', 'ProgressAgent',
    'RecommendationAgent', 'MemoryAgent', 'OrchestratorAgent',
])
