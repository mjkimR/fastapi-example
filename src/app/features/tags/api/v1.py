import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.features.auth.deps import get_current_user
from app.features.tags.schemas import TagRead
from app.features.tags.usecases.crud import (
    GetMultiTagUseCase,
    GetTagUseCase,
)
from app_base.base.deps.params.page import PaginationParam
from app_base.base.exceptions.basic import NotFoundException
from app_base.base.schemas.paginated import PaginatedList

router = APIRouter(
    prefix="/workspaces/{workspace_id}/tags",
    tags=["Tags"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=PaginatedList[TagRead])
async def get_tags(
    use_case: Annotated[GetMultiTagUseCase, Depends()],
    workspace_id: uuid.UUID,
    pagination: PaginationParam,
):
    return await use_case.execute(**pagination, context={"parent_id": workspace_id})


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(
    use_case: Annotated[GetTagUseCase, Depends()],
    workspace_id: uuid.UUID,
    tag_id: uuid.UUID,
):
    tag = await use_case.execute(tag_id, context={"parent_id": workspace_id})
    if not tag:
        raise NotFoundException()
    return tag
