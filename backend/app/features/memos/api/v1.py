import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from app.base.deps.params.page import PaginationParam
from app.base.exceptions.basic import NotFoundException
from app.base.schemas.delete_resp import DeleteResponse
from app.base.schemas.paginated import PaginatedList
from app.features.auth.deps import get_current_user
from app.features.auth.models import User
from app.features.memos.schemas import MemoCreate, MemoRead, MemoUpdate
from app.features.memos.usecases.crud import (
    CreateMemoUseCase,
    DeleteMemoUseCase,
    GetMemoUseCase,
    GetMultiMemoUseCase,
    UpdateMemoUseCase,
)

router = APIRouter(
    prefix="/workspaces/{workspace_id}/memos",
    tags=["Memos"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=MemoRead)
async def create_memo(
    use_case: Annotated[CreateMemoUseCase, Depends()],
    workspace_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    memo_in: Annotated[MemoCreate, Body()],
):
    return await use_case.execute(memo_in, context={"parent_id": workspace_id, "user_id": current_user.id})


@router.get("", response_model=PaginatedList[MemoRead])
async def get_memos(
    use_case: Annotated[GetMultiMemoUseCase, Depends()],
    workspace_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: PaginationParam,
):
    return await use_case.execute(**pagination, context={"parent_id": workspace_id, "user_id": current_user.id})


@router.get("/{memo_id}", response_model=MemoRead)
async def get_memo(
    use_case: Annotated[GetMemoUseCase, Depends()],
    workspace_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    memo_id: uuid.UUID,
):
    memo = await use_case.execute(memo_id, context={"parent_id": workspace_id, "user_id": current_user.id})
    if not memo:
        raise NotFoundException()
    return memo


@router.put("/{memo_id}", response_model=MemoRead)
async def update_memo(
    use_case: Annotated[UpdateMemoUseCase, Depends()],
    workspace_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    memo_id: uuid.UUID,
    memo_in: MemoUpdate,
):
    memo = await use_case.execute(
        memo_id,
        memo_in,
        context={"parent_id": workspace_id, "user_id": current_user.id},
    )
    if not memo:
        raise NotFoundException()
    return memo


@router.delete("/{memo_id}", response_model=DeleteResponse)
async def delete_memo(
    use_case: Annotated[DeleteMemoUseCase, Depends()],
    workspace_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    memo_id: uuid.UUID,
):
    return await use_case.execute(memo_id, context={"parent_id": workspace_id, "user_id": current_user.id})
