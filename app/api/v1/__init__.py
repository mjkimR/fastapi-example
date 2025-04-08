from fastapi import APIRouter

from app.api.v1.memo import router as memo_router

router = APIRouter(prefix="/v1")
router.include_router(memo_router)
