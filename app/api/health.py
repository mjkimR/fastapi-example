from fastapi import APIRouter
from starlette.responses import Response

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", status_code=204)
async def health():
    return Response(status_code=204)
