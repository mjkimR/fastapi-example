from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.deps.params.page import PaginationParam
from app.schemas.base import PaginatedList
from app.schemas.tags import TagRead
from app.usecase.tags.crud import GetMultiTagUseCase

router = APIRouter(
    prefix="/tags", tags=["Tags"], dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=PaginatedList[TagRead])
async def get_tags(
    use_case: Annotated[GetMultiTagUseCase, Depends()],
    pagination: PaginationParam,
):
    tags = await use_case.execute(**pagination)
    return tags
