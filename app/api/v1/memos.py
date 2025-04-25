import uuid

from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.schemas.memo import MemoRead, MemoUpdate, MemoCreate, MemosRead
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


@router.get("/", response_model=MemosRead)
async def get_memos(
        offset: int = Query(0, ge=0),
        limit: int = Query(100, gt=0, le=1000),
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memos = await service.get_multi(session, offset=offset, limit=limit)
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
