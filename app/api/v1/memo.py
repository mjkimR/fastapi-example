import uuid

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.memo import MemoRead, MemoUpdate, MemoCreate, MemosRead
from app.core.deps.session import get_session
from app.services.memo import MemoService

router = APIRouter(prefix="/memos", tags=["Memo"])


@router.post("/", response_model=MemoRead)
async def create_memo(
        memo_in: MemoCreate = Body(...),
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    """Create a new memo."""
    memo = await service.create(session, memo_in)
    return memo


@router.get("/", response_model=MemosRead)
async def get_memos(
        offset: int = 0,
        limit: int = 100,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    """Retrieve a list of memos."""
    memos = await service.get_multi(session, offset=offset, limit=limit)
    return memos


@router.get("/{memo_id}", response_model=MemoRead)
async def get_memo(
        memo_id: uuid.UUID,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    """Retrieve a memo by its ID."""
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
    """Update an existing memo by its ID."""
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
    """Delete a memo by its ID."""
    if await service.delete_by_id(session, memo_id):
        return {"detail": f"Memo with id {memo_id} has been deleted"}
    else:
        raise HTTPException(status_code=404, detail="Not found")
