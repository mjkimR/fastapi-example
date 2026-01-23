from typing import Annotated

from fastapi import APIRouter, Depends

from app.features.auth.deps import get_current_user
from app.core.deps.params.page import PaginationParam
from app.base.schemas.paginated import PaginatedList
from app.features.tags.schemas import TagRead
from app.features.tags.usecases.crud import GetMultiTagUseCase

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
