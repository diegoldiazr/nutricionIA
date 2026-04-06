from .users import router as users_router
from .meals import router as meals_router
from .nutrition import router as nutrition_router
from .progress import router as progress_router

__all__ = ["users_router", "meals_router", "nutrition_router", "progress_router"]
