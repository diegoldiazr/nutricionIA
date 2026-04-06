"""
Base Agent - Abstract base class for all agents in the system.

All agents must inherit from this class. Provides standard lifecycle,
health checking, and event publishing capabilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
from core.events import EventBus, EventType, Event
from core.exceptions import AgentError


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Implements the standard agent interface:
    - Lifecycle: initialize(), shutdown()
    - Health: health()
    - Processing: process(request) (abstract)

    Agents should NOT hold direct references to other agents.
    Use event_bus.publish() for communication.
    """

    def __init__(self, agent_id: str, name: str, event_bus: EventBus = None):
        """
        Initialize agent.

        Args:
            agent_id: Unique identifier for this agent instance
            name: Human-readable name
            event_bus: Shared event bus instance
        """
        self.agent_id = agent_id
        self.name = name
        self.event_bus = event_bus
        self._initialized = False
        self._orchestrator: Optional[Any] = None  # Forward reference to orchestrator

    @property
    def orchestrator(self) -> Any:
        """Get the orchestrator instance (set by orchestrator after creation)."""
        return self._orchestrator

    @orchestrator.setter
    def orchestrator(self, value: Any):
        """Set orchestrator reference (for routing requests)."""
        self._orchestrator = value

    async def initialize(self) -> None:
        """
        Called during system startup.
        Override to perform agent-specific initialization.
        """
        self._initialized = True
        if self.event_bus:
            await self.event_bus.publish(Event(
                event_type=EventType.AGENT_INITIALIZED,
                source=self.agent_id,
                payload={'agent_name': self.name}
            ))

    async def shutdown(self) -> None:
        """
        Called during system shutdown.
        Override to perform cleanup.
        """
        self._initialized = False
        if self.event_bus:
            await self.event_bus.publish(Event(
                event_type=EventType.AGENT_SHUTDOWN,
                source=self.agent_id,
                payload={'agent_name': self.name}
            ))

    async def health(self) -> Dict[str, Any]:
        """
        Health check for this agent.

        Returns:
            Dict with status, timestamp, and optional details
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
            request: Dict containing the request data.
                Must include 'action' key.

        Returns:
            Dict with the response data
        """
        pass

    def _validate_request(self, request: Dict[str, Any], required_fields: list) -> None:
        """Validate request has required fields."""
        missing = [f for f in required_fields if f not in request]
        if missing:
            raise AgentError(f"Missing required fields: {missing}")

    def _publish_event(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        """
        Publish an event (non-blocking).

        Args:
            event_type: Event type enum
            payload: Event payload data
        """
        if self.event_bus:
            # Fire and forget - event bus handles async
            import asyncio
            asyncio.create_task(self.event_bus.publish(Event(
                event_type=event_type,
                source=self.agent_id,
                payload=payload
            )))

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.agent_id})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(agent_id={self.agent_id})>"
