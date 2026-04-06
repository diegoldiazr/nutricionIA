"""Services module - Business logic services."""


from .openrouter_service import OpenRouterService
from .notebooklm_service import NotebookLMService

# Backward compatibility alias
NotebookLMConnector = NotebookLMService

__all__ = [
    'OpenRouterService',
    'NotebookLMService',
    'NotebookLMConnector',  # For backward compatibility
]
