from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app_base.core.database.deps import get_session
from app.features.auth.api import v1_admin_router, v1_login_router, v1_users_router
from app.features.memos.api.v1 import router as v1_memos_router
from app.features.tags.api.v1 import router as v1_tags_router
from app.features.workspaces.api.v1 import router as v1_workspaces_router

router = APIRouter(prefix="/api")
v1_router = APIRouter(prefix="/v1")


@router.get("/health", status_code=204)
async def health():
    return Response(status_code=204)


@router.get("/health/deep", status_code=status.HTTP_200_OK)
async def deep_health_check(session: Annotated[AsyncSession, Depends(get_session)]):
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return Response(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content="Database connection failed",
        )


# Feature routers
v1_router.include_router(v1_admin_router)
v1_router.include_router(v1_users_router)
v1_router.include_router(v1_login_router)
v1_router.include_router(v1_workspaces_router)
v1_router.include_router(v1_memos_router)
v1_router.include_router(v1_tags_router)

router.include_router(v1_router)
