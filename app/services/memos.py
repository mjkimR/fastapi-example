from fastapi import Depends

from app.models.memos import Memo
from app.repos.memos import MemoRepository
from app.schemas.memo import MemoCreate, MemoUpdate
from app.services.base import BaseService


class MemoService(BaseService[MemoRepository, Memo, MemoCreate, MemoUpdate]):
    """Service class for handling memo-related operations."""

    def __init__(self, repo: MemoRepository = Depends(MemoRepository.get_repo)):
        super().__init__(repo)
