from fastapi import APIRouter

from api.health import router as health_router
from api.v1 import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
router.include_router(health_router)
