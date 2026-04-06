"""
Base Agent - Abstract base class for all agents in the system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class that all agents must inherit from.
    Defines the common interface and lifecycle methods.
    """

    def __init__(self, agent_id: str, name: str):
        """
        Initialize the agent.

        Args:
            agent_id: Unique identifier for this agent instance
            name: Human-readable name
        """
        self.agent_id = agent_id
        self.name = name
        self._orchestrator = None
        self._initialized = False

    @property
    def orchestrator(self) -> 'OrchestratorAgent':
        """Get the orchestrator instance."""
        return self._orchestrator

    @orchestrator.setter
    def orchestrator(self, value: 'OrchestratorAgent'):
        """Set the orchestrator reference."""
        self._orchestrator = value

    async def initialize(self) -> None:
        """
        Called during system startup.
        Override to perform any initialization logic.
        """
        self._initialized = True

    async def shutdown(self) -> None:
        """
        Called during system shutdown.
        Override to perform cleanup.
        """
        self._initialized = False

    async def health(self) -> Dict[str, Any]:
        """
        Health check for this agent.

        Returns:
            Dict with status, message, and timestamp
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": "healthy" if self._initialized else "uninitialized",
            "timestamp": datetime.utcnow().isoformat()
        }

    @abstractmethod
    async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - must be implemented by each agent.

        Args:
            request: Dict containing the request data

        Returns:
            Dict with the response data
        """
        pass

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.agent_id})"
