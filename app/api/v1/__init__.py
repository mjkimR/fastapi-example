from fastapi import APIRouter

from app.api.v1.memos import router as memo_router
from app.api.v1.auth.login import router as login_router
from app.api.v1.auth.users import router as user_router

router = APIRouter(prefix="/v1")
router.include_router(memo_router)
router.include_router(login_router)
router.include_router(user_router)
