from app.models.memo import Memo
from app.repos.base import BaseRepository
from app.schemas.memo import MemoCreate, MemoUpdate


class MemoRepository(BaseRepository[Memo, MemoCreate, MemoUpdate]):
    """Repository for Memo model."""

    @staticmethod
    def get_repo() -> "MemoRepository":
        """Get an instance of MemoRepository."""
        return MemoRepository(
            model=Memo,
            default_order_by_col="updated_at",
        )
