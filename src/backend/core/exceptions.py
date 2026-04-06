"""
Custom Exceptions - Application-specific error types for clear error handling.
"""


class NutritionAppError(Exception):
    """Base exception for all nutrition assistant errors."""
    pass


class ConfigurationError(NutritionAppError):
    """Configuration loading or validation error."""
    pass


class DatabaseError(NutritionAppError):
    """Database operation error."""
    pass


class AgentError(NutritionAppError):
    """Agent processing error."""
    pass


class ServiceError(NutritionAppError):
    """External service (OpenRouter, NotebookLM) error."""
    pass


class ValidationError(NutritionAppError):
    """Data validation error."""
    pass


class NotFoundError(NutritionAppError):
    """Resource not found error."""
    pass


class ConflictError(NutritionAppError):
    """Resource conflict error (e.g., duplicate email)."""
    pass
