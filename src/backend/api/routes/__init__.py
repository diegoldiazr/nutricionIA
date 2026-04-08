"""API routes."""
from fastapi import APIRouter

# Import individual routers from each module
from .health import router as health_router
from .profiles import router as profiles_router
from .meals import router as meals_router
from .nutrition import router as nutrition_router
from .progress import router as progress_router
from .dashboard import router as dashboard_router

# Create main router that combines all endpoints
router = APIRouter(prefix="/api/v1")

# Include all sub-routers
router.include_router(health_router)
router.include_router(profiles_router)
router.include_router(meals_router)
router.include_router(nutrition_router)
router.include_router(progress_router)
router.include_router(dashboard_router)

__all__ = ['router']
