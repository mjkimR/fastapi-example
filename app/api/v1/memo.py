import uuid

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.memo import MemoRead, MemoUpdate, MemoCreate, MemosRead
from app.core.deps.session import get_session
from app.services.memo import MemoService

router = APIRouter(prefix="/memos", tags=["Memo"])


@router.post("/", response_model=MemoRead)
async def create_memo(
        memo: MemoCreate = Body(...),
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    created_memo = await service.create(session, memo)
    return created_memo


@router.get("/", response_model=MemosRead)
async def get_memos(
        offset: int = 0,
        limit: int = 100,
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
        memo_update: MemoUpdate,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memo = await service.update_by_id(session, memo_id, memo_update)
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
