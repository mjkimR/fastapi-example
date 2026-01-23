from starlette.responses import Response

from fastapi import APIRouter
from app.features.auth.api import v1_admin_router, v1_users_router, v1_login_router
from app.features.tags.api import v1_tags_router
from app.features.memos.api import v1_memos_router

router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")


@router.get("/health", status_code=204)
async def health():
    return Response(status_code=204)


# Feature routers
v1_router.include_router(v1_admin_router)
v1_router.include_router(v1_users_router)
v1_router.include_router(v1_login_router)
v1_router.include_router(v1_tags_router)
v1_router.include_router(v1_memos_router)

router.include_router(v1_router)
