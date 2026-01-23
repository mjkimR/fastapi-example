from app.base.deps.ordering.base import order_by_for
from app.base.deps.ordering.combine import create_order_by_dependency
from app.features.memos.models import Memo


@order_by_for(alias="title")
def order_by_title(desc: bool):
    """Order by title"""
    return Memo.title.desc() if desc else Memo.title.asc()


@order_by_for(alias="created_at")
def order_by_created_at(desc: bool):
    """Order by created_at"""
    return Memo.created_at.desc() if desc else Memo.created_at.asc()


@order_by_for(alias="id")
def order_by_id(desc: bool):
    """Order by id"""
    return Memo.id.desc() if desc else Memo.id.asc()


MemoOrderByDepend = create_order_by_dependency(
    order_by_title, order_by_created_at, order_by_id,
    default_order="-created_at,id",
    tie_breaker=order_by_id,
)
