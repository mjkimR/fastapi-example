from fastapi import APIRouter

from api.v1.example import router as example_router

router = APIRouter(prefix="/v1")
router.include_router(example_router)
