"""
Message Bus - Simple pub/sub for inter-agent communication.
"""
from typing import Any, Callable, Dict, List
from datetime import datetime
import uuid


class Message:
    """Represents a message between agents."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: str = None,
        timestamp: datetime = None
    ):
        self.message_id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.correlation_id = correlation_id or self.message_id
        self.timestamp = timestamp or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "message_type": self.message_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat()
        }


class MessageBus:
    """
    Simple in-memory message bus for agent communication.
    Supports pub/sub pattern.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._history: List[Message] = []

    async def publish(self, message: Message) -> None:
        """
        Publish a message to the bus.

        Args:
            message: Message to publish
        """
        self._history.append(message)

        # Notify subscribers for this message type
        if message.message_type in self._subscribers:
            for callback in self._subscribers[message.message_type]:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error in message callback: {e}")

        # Also notify wildcard subscribers
        if "*" in self._subscribers:
            for callback in self._subscribers["*"]:
                try:
                    await callback(message)
                except Exception as e:
                    print(f"Error in wildcard callback: {e}")

    def subscribe(self, message_type: str, callback: Callable) -> None:
        """
        Subscribe to a specific message type.

        Args:
            message_type: Type of message to subscribe to (or "*" for all)
            callback: Async function to call when message received
        """
        if message_type not in self._subscribers:
            self._subscribers[message_type] = []
        self._subscribers[message_type].append(callback)

    def unsubscribe(self, message_type: str, callback: Callable) -> None:
        """Unsubscribe from a message type."""
        if message_type in self._subscribers:
            try:
                self._subscribers[message_type].remove(callback)
            except ValueError:
                pass

    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent message history."""
        return [msg.to_dict() for msg in self._history[-limit:]]
