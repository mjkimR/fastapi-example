from app.base.filters.base import SimpleFilterCriteriaBase
from app.base.filters.decorators import filter_for
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


class FilterTitle(SimpleFilterCriteriaBase):
    def _filter_logic(self, value):
        """
        Filter Memos by field 'title'
        """
        return Memo.title.ilike(f"%{value}%")
