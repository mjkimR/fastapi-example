import uuid

from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.deps.filters.base import create_combined_filter_dependency
from app.core.deps.filters.generic.criteria_ilike import GenericILikeCriteria
from app.core.deps.params.order_by import order_by_params
from app.core.deps.params.page import PaginationParam
from app.models.memo import Memo
from app.schemas.base import PaginatedList
from app.schemas.memo import MemoRead, MemoUpdate, MemoCreate
from app.core.deps.session import get_session
from app.services.memo import MemoService

router = APIRouter(prefix="/memos", tags=["Memos"], dependencies=[Depends(get_current_user)])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MemoRead)
async def create_memo(
        memo_in: MemoCreate = Body(...),
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memo = await service.create(session, memo_in)
    return memo


@router.get("/", response_model=PaginatedList[MemoRead])
async def get_memos(
        pagination: PaginationParam,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
        order_by=Depends(order_by_params(Memo)),
        filters=Depends(create_combined_filter_dependency(
            GenericILikeCriteria("title", "title"),
            GenericILikeCriteria("category", "category"),
            orm_model=Memo,
        ))
):
    memos = await service.get_multi(
        session, order_by=order_by, filters=filters, **pagination
    )
    return memos


@router.get("/{memo_id}", response_model=MemoRead)
async def get_memo(
        memo_id: uuid.UUID,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memo = await service.get_by_id(session, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Not found")
    return memo


@router.put("/{memo_id}", response_model=MemoRead)
async def update_memo(
        memo_id: uuid.UUID,
        memo_in: MemoUpdate,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memo = await service.update_by_id(session, memo_id, memo_in)
    if not memo:
        raise HTTPException(status_code=404, detail="Not found")
    return memo


@router.delete("/{memo_id}")
async def delete_memo(
        memo_id: uuid.UUID,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    if await service.delete_by_id(session, memo_id):
        return {"detail": f"Memo with id {memo_id} has been deleted"}
    else:
        raise HTTPException(status_code=404, detail="Not found")
