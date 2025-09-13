from typing import Annotated

from fastapi import Depends

from app.models.memos import Memo
from app.repos.memos import MemoRepository
from app.schemas.memos import MemoCreate, MemoUpdate
from app.services.base.basic import (
    BasicGetMultiServiceMixin, BasicGetServiceMixin, BasicDeleteServiceMixin, BasicUpdateServiceMixin,
    BasicCreateServiceMixin
)


class MemoService(
    BasicGetServiceMixin[MemoRepository, Memo],
    BasicGetMultiServiceMixin[MemoRepository, Memo],
    BasicCreateServiceMixin[MemoRepository, Memo, MemoCreate],
    BasicUpdateServiceMixin[MemoRepository, Memo, MemoUpdate],
    BasicDeleteServiceMixin[MemoRepository, Memo]
):
    """Service class for handling memo-related operations."""

    def __init__(self, repo: Annotated[MemoRepository, Depends()]):
        self.repo = repo
