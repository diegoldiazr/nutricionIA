"""
Agent Factory - Creates and wires agents with proper dependencies.

Centralizes agent instantiation and initialization order.
"""

from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
from core.events import EventBus
from core.exceptions import AgentError
import asyncio


class AgentFactory:
    """
    Factory for creating and initializing agents.

    Handles dependency injection and initialization order.
    """
    
    def __init__(self, event_bus: EventBus):
        """
        Initialize factory.

        Args:
            event_bus: Shared event bus instance
        """
        self.event_bus = event_bus
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._dependency_graph: Dict[str, List[str]] = {}
    
    def register(
        self,
        agent_id: str,
        agent_class: type,
        config: Dict[str, Any] = None,
        dependencies: List[str] = None
    ) -> None:
        """
        Register an agent class with the factory.

        Args:
            agent_id: Unique identifier for agent
            agent_class: Agent class (subclass of BaseAgent)
            config: Agent-specific configuration
            dependencies: List of agent_ids this agent depends on
        """
        self._registry[agent_id] = {
            'class': agent_class,
            'config': config or {},
        }
        if dependencies:
            self._dependency_graph[agent_id] = dependencies
    
    async def create_all(
        self,
        shared_dependencies: Dict[str, Any] = None
    ) -> Dict[str, BaseAgent]:
        """
        Create all registered agents with proper dependency order.

        Args:
            shared_dependencies: Dict of shared dependencies (db_service, etc.)

        Returns:
            Dict mapping agent_id to agent instance
        """
        shared_deps = shared_dependencies or {}
        agents: Dict[str, BaseAgent] = {}
        created = set()

        # Determine creation order based on dependencies
        ordered_ids = self._topological_sort() or list(self._registry.keys())

        for agent_id in ordered_ids:
            info = self._registry[agent_id]
            
            # Build kwargs from dependencies that have been created
            kwargs = {}
            
            # Add class-specific config
            kwargs.update(info['config'])
            
            # Add agent instance dependencies
            if agent_id in self._dependency_graph:
                for dep_id in self._dependency_graph[agent_id]:
                    if dep_id not in agents:
                        raise AgentError(f"Dependency '{dep_id}' not created for agent '{agent_id}'")
                    # Map dependency agent_id to appropriate parameter name
                    param_name = f"{dep_id}_agent"
                    kwargs[param_name] = agents[dep_id]
            
            # Add shared dependencies (db_service, openrouter, etc.)
            kwargs.update(shared_deps)
            
            # Always provide event_bus
            if 'event_bus' not in kwargs:
                kwargs['event_bus'] = self.event_bus

            # Create agent instance
            agent = info['class'](agent_id=agent_id, **kwargs)
            agents[agent_id] = agent

        # Initialize all agents after creation
        for agent in agents.values():
            await agent.initialize()

        return agents
    
    def _topological_sort(self) -> Optional[List[str]]:
        """
        Sort agents by dependency order (topological sort).
        
        Returns:
            List of agent IDs in dependency order, or None if cycle detected
        """
        if not self._dependency_graph:
            return None
        
        # Simple DFS-based topological sort
        visited = set()
        temp = set()
        order = []

        def visit(node: str) -> bool:
            if node in temp:
                return False  # cycle detected
            if node in visited:
                return True
            
            temp.add(node)
            for dep in self._dependency_graph.get(node, []):
                if not visit(dep):
                    return False
            temp.remove(node)
            visited.add(node)
            order.append(node)
            return True

        for node in self._registry.keys():
            if node not in visited:
                if not visit(node):
                    return None  # cycle
        
        return list(reversed(order))  # Reverse to get correct order
    
    def clear(self) -> None:
        """Clear all registered agents."""
        self._registry.clear()
        self._dependency_graph.clear()


# Helper functions for common agent creation
def create_agent_factory(event_bus: EventBus) -> AgentFactory:
    """
    Create and configure the agent factory with all agents.

    Args:
        event_bus: Shared event bus instance

    Returns:
        Configured AgentFactory instance
    """
    from .knowledge_agent.agent import KnowledgeAgent
    from .user_agent.agent import UserAgent
    from .nutrition_agent.agent import NutritionAgent
    from .meal_planner_agent.agent import MealPlannerAgent
    from .recipe_agent.agent import RecipeAgent
    from .progress_agent.agent import ProgressAgent
    from .recommendation_agent.agent import RecommendationAgent
    from .memory_agent.agent import MemoryAgent
    from .orchestrator_agent.agent import OrchestratorAgent

    factory = AgentFactory(event_bus)

    # Register all agents with their dependencies
    # No direct dependencies first
    factory.register('knowledge', KnowledgeAgent, config={'max_retries': 3})
    factory.register('user', UserAgent)
    
    # Nutrition depends on knowledge
    factory.register(
        'nutrition',
        NutritionAgent,
        dependencies=['knowledge']
    )
    
    # Memory depends on user, database (via shared deps)
    factory.register('memory', MemoryAgent)
    
    # Meal planner depends on knowledge, user
    factory.register(
        'meal_planner',
        MealPlannerAgent,
        dependencies=['knowledge', 'user']
    )
    
    # Recipe depends on knowledge, meal_planner (circular - will be resolved post-creation)
    factory.register(
        'recipe',
        RecipeAgent,
        dependencies=['knowledge', 'meal_planner']
    )
    
    # Progress agent depends on user and nutrition
    factory.register(
        'progress',
        ProgressAgent,
        dependencies=['user', 'nutrition']
    )
    
    # Recommendation depends on nutrition, progress, user, memory
    factory.register(
        'recommendation',
        RecommendationAgent,
        dependencies=['nutrition', 'progress', 'user', 'memory']
    )
    
    # Orchestrator depends on all
    factory.register(
        'orchestrator',
        OrchestratorAgent,
        dependencies=[
            'knowledge', 'nutrition', 'user', 'meal_planner',
            'recipe', 'progress', 'recommendation', 'memory'
        ]
    )

    return factory
