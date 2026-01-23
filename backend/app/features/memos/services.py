from typing import Annotated

from fastapi import Depends

from app.features.memos.models import Memo
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.base.services.base import (
    BaseCRUDServiceMixin, BaseContextKwargs
)


class MemoService(
    BaseCRUDServiceMixin[MemoRepository, Memo, MemoCreate, MemoUpdate, BaseContextKwargs],
):
    """Service class for handling memo-related operations."""

    def __init__(self, repo: Annotated[MemoRepository, Depends()]):
        self.repo = repo
