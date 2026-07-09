from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .games import router as games_router
from .models import router as models_router
from .admin import router as admin_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(games_router)
router.include_router(models_router)
router.include_router(admin_router)
