from typing import Annotated

from fastapi import Depends

from app.models.memos import Memo
from app.repos.memos import MemoRepository
from app.schemas.memos import MemoCreate, MemoUpdate
from app.services.base.base import (
    BaseCRUDServiceMixin, BaseContextKwargs
)


class MemoService(
    BaseCRUDServiceMixin[MemoRepository, Memo, MemoCreate, MemoUpdate, BaseContextKwargs],
):
    """Service class for handling memo-related operations."""

    def __init__(self, repo: Annotated[MemoRepository, Depends()]):
        self.repo = repo
