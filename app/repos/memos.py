from app.models.memos import Memo
from app.repos.base import BaseRepository
from app.schemas.memos import MemoCreate, MemoUpdate


class MemoRepository(BaseRepository[Memo, MemoCreate, MemoUpdate]):
    """Repository for Memo model."""
    model = Memo
