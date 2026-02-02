from app.features.memos.models import Memo
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app_base.base.repos.base import BaseRepository


class MemoRepository(BaseRepository[Memo, MemoCreate, MemoUpdate]):
    """Repository for Memo model."""

    model = Memo
