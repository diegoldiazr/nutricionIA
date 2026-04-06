"""Database repositories package."""

from typing import Dict, Any

from .base import BaseRepository
from .user_repository import UserRepository
from .macro_repository import MacroRepository
from .preference_repository import PreferenceRepository
from .memory_repository import MemoryRepository

__all__ = [
    'BaseRepository',
    'UserRepository',
    'MacroRepository',
    'PreferenceRepository',
    'MemoryRepository',
]

# Repository factory for dependency injection
def get_repositories(session) -> Dict[str, Any]:
    """
    Create all repositories with the same session.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        Dict mapping repository names to instances
    """
    return {
        'users': UserRepository(session),
        'macros': MacroRepository(session),
        'preferences': PreferenceRepository(session),
        'memory': MemoryRepository(session),
    }
