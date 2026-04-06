"""
Event System - Decoupled communication between agents and components.

This module provides:
- Typed event definitions
- Event bus for pub/sub pattern
- Standardized event payloads

Agents publish events instead of calling each other directly.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Awaitable, Optional
from enum import Enum
from datetime import datetime
import uuid
from collections import defaultdict


class EventType(Enum):
    """Standard event types in the system."""
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    PROFILE_UPDATED = "profile.updated"

    # Meal events
    MEAL_LOGGED = "meal.logged"
    MEAL_UPDATED = "meal.updated"
    MEAL_DELETED = "meal.deleted"

    # Nutrition events
    TARGETS_CALCULATED = "targets.calculated"
    MACROS_UPDATED = "macros.updated"

    # Agent events
    AGENT_INITIALIZED = "agent.initialized"
    AGENT_SHUTDOWN = "agent.shutdown"
    AGENT_ERROR = "agent.error"

    # System events
    SYSTEM_HEALTH_CHECK = "system.health_check"
    CONFIGURATION_LOADED = "config.loaded"


@dataclass
class Event:
    """Base event class. Every event must include source, payload, timestamp, and unique ID."""
    event_type: EventType
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())


class EventBus:
    """
    Central event bus for pub/sub communication. Eliminates direct agent references.

    Usage:
        bus = EventBus()
        bus.subscribe(EventType.USER_CREATED, my_handler)
        await bus.publish(Event(event_type=EventType.USER_CREATED, source="user_agent", payload={...}))
    """

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._history: List[Event] = []
        self._max_history_size: int = 1000

    def subscribe(self, event_type: EventType, handler: Callable[[Event], Awaitable[None]]) -> None:
        """Subscribe to an event type. Handler must be async."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Remove a handler from an event type."""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
            except ValueError:
                pass

    async def publish(self, event: Event) -> None:
        """Publish event to all subscribers. Subscriber errors are caught and ignored."""
        self._history.append(event)
        if len(self._history) > self._max_history_size:
            self._history.pop(0)

        import asyncio
        handlers = self._subscribers.get(event.event_type, [])
        wildcard_handlers = self._subscribers.get(None, [])
        all_handlers = handlers + wildcard_handlers

        if all_handlers:
            tasks = [handler(event) for handler in all_handlers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    import logging
                    logging.getLogger(__name__).warning(f"Event handler error: {result}")

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Get recent event history, most recent first."""
        if event_type:
            filtered = [e for e in self._history if e.event_type == event_type]
        else:
            filtered = self._history.copy()
        return filtered[-limit:][::-1]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()

    @property
    def subscriber_count(self) -> int:
        """Get total number of subscribers."""
        return sum(len(handlers) for handlers in self._subscribers.values())


# Global event bus instance - use this everywhere
event_bus = EventBus()
