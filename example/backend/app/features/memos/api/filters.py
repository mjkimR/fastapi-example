from app_kit.base.deps.filters.combine import create_combined_filter_dependency
from app_kit.base.deps.filters.decorators import filter_for
from app.features.memos.models import Memo


@filter_for(bound_type=str)
def filter_title(value):
    """
    Filter Memos by field 'title'
    """
    if value is None:
        return None
    return Memo.title.ilike(f"%{value}%")


@filter_for(bound_type=str)
def filter_category(value):
    """
    Filter Memos by field 'category'
    """
    if value is None:
        return None
    return Memo.category.ilike(f"%{value}%")


MemoFilterDepend = create_combined_filter_dependency(filter_title, filter_category)
