from app.base.deps.filters.combine import create_combined_filter_dependency
from app.base.deps.filters.decorators import filter_for
from app.features.memos.models import Memo


@filter_for(bound_type=str)
def filter_title(value):
    """
    Filter Memos by field 'title'
    """
    return Memo.title.ilike(f"%{value}%")


@filter_for(bound_type=str)
def filter_category(value):
    """
    Filter Memos by field 'category'
    """
    return Memo.category.ilike(f"%{value}%")


MemoFilterDepend = create_combined_filter_dependency(filter_title, filter_category)
