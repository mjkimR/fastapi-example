from app.features.memos.api.order_by import (
    order_by_created_at,
    order_by_id,
    order_by_title,
)
from app_base.base.deps.ordering.base import OrderByCriteria


class TestOrderByTitle:
    """Tests for order_by_title."""

    def test_is_order_by_criteria(self):
        """Should be an OrderByCriteria instance."""
        assert isinstance(order_by_title, OrderByCriteria)

    def test_alias_is_title(self):
        """Should have alias 'title'."""
        assert order_by_title.alias == "title"

    def test_returns_desc_expression(self):
        """Should return desc expression when desc=True."""
        result = order_by_title(desc=True)
        assert result is not None

    def test_returns_asc_expression(self):
        """Should return asc expression when desc=False."""
        result = order_by_title(desc=False)
        assert result is not None


class TestOrderByCreatedAt:
    """Tests for order_by_created_at."""

    def test_is_order_by_criteria(self):
        """Should be an OrderByCriteria instance."""
        assert isinstance(order_by_created_at, OrderByCriteria)

    def test_alias_is_created_at(self):
        """Should have alias 'created_at'."""
        assert order_by_created_at.alias == "created_at"

    def test_returns_desc_expression(self):
        """Should return desc expression when desc=True."""
        result = order_by_created_at(desc=True)
        assert result is not None

    def test_returns_asc_expression(self):
        """Should return asc expression when desc=False."""
        result = order_by_created_at(desc=False)
        assert result is not None


class TestOrderById:
    """Tests for order_by_id."""

    def test_is_order_by_criteria(self):
        """Should be an OrderByCriteria instance."""
        assert isinstance(order_by_id, OrderByCriteria)

    def test_alias_is_id(self):
        """Should have alias 'id'."""
        assert order_by_id.alias == "id"

    def test_returns_desc_expression(self):
        """Should return desc expression when desc=True."""
        result = order_by_id(desc=True)
        assert result is not None

    def test_returns_asc_expression(self):
        """Should return asc expression when desc=False."""
        result = order_by_id(desc=False)
        assert result is not None
