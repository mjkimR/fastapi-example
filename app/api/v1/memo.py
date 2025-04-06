import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.memo import MemoRead, MemoUpdate, MemoCreate
from core.deps.session import get_session
from services.memo import MemoService

router = APIRouter(prefix="/memos", tags=["Memo"])


@router.post("/", response_model=MemoRead)
def create_memo(
        memo: MemoCreate,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    return service.create(session, memo)


@router.get("/", response_model=list[MemoRead])
def get_memos(

):
    raise NotImplementedError


@router.get("/{memo_id}", response_model=MemoRead)
def get_memo(
        memo_id: uuid.UUID,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memo = service.get(session, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Not found")
    return memo


@router.put("/{memo_id}", response_model=MemoRead)
def update_memo(
        memo_id: uuid.UUID,
        memo_update: MemoUpdate,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    memo = service.update(session, memo_id, memo_update)
    if not memo:
        raise HTTPException(status_code=404, detail="Not found")
    return memo


@router.delete("/{memo_id}")
def delete_memo(
        memo_id: uuid.UUID,
        session: AsyncSession = Depends(get_session),
        service: MemoService = Depends(),
):
    service.delete(session, memo_id)
    return {"detail": f"Memo with id {memo_id} has been deleted"}
