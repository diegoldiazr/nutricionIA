"""API routes."""
from .health import router as health_router
from .profiles import router as profiles_router
from .meals import router as meals_router
from .nutrition import router as nutrition_router
from .progress import router as progress_router
from .dashboard import router as dashboard_router

__all__ = [
    'health_router',
    'profiles_router',
    'meals_router',
    'nutrition_router',
    'progress_router',
    'dashboard_router',
]
