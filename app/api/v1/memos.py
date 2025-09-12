import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body, status

from app.core.deps.auth import get_current_user
from app.core.deps.filters.base import create_combined_filter_dependency
from app.core.deps.filters.generic.criteria_ilike import GenericILikeCriteria
from app.core.deps.params.order_by import order_by_params
from app.core.deps.params.page import PaginationParam
from app.models.memos import Memo
from app.schemas.base import PaginatedList
from app.schemas.memos import MemoRead, MemoUpdate, MemoCreate
from app.usecase.memos.crud import (
    CreateMemoUseCase,
    GetMemoUseCase,
    GetMultiMemoUseCase,
    UpdateMemoUseCase,
    DeleteMemoUseCase,
)

router = APIRouter(
    prefix="/memos", tags=["Memos"], dependencies=[Depends(get_current_user)]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MemoRead)
async def create_memo(
        use_case: Annotated[CreateMemoUseCase, Depends()],
        memo_in: MemoCreate = Body(),
):
    memo = await use_case.execute(memo_in)
    return memo


@router.get("/", response_model=PaginatedList[MemoRead])
async def get_memos(
        use_case: Annotated[GetMultiMemoUseCase, Depends()],
        pagination: PaginationParam,
        order_by=Depends(order_by_params(Memo)),
        filters=Depends(
            create_combined_filter_dependency(
                GenericILikeCriteria("title", "title"),
                GenericILikeCriteria("category", "category"),
                orm_model=Memo,
            )
        ),
):
    memos = await use_case.execute(order_by=order_by, where=filters, **pagination)
    return memos


@router.get("/{memo_id}", response_model=MemoRead)
async def get_memo(
        use_case: Annotated[GetMemoUseCase, Depends()],
        memo_id: uuid.UUID,
):
    memo = await use_case.execute(memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Not found")
    return memo


@router.put("/{memo_id}", response_model=MemoRead)
async def update_memo(
        use_case: Annotated[UpdateMemoUseCase, Depends()],
        memo_id: uuid.UUID,
        memo_in: MemoUpdate,
):
    memo = await use_case.execute(memo_id, memo_in)
    if not memo:
        raise HTTPException(status_code=404, detail="Not found")
    return memo


@router.delete("/{memo_id}")
async def delete_memo(
        use_case: Annotated[DeleteMemoUseCase, Depends()],
        memo_id: uuid.UUID,
):
    if await use_case.execute(memo_id):
        return {"detail": f"Memo with id {memo_id} has been deleted"}
    else:
        raise HTTPException(status_code=404, detail="Not found")
