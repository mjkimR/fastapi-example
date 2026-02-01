from app.features.memos.api.filters import filter_category, filter_title


class TestFilterTitle:
    """Tests for filter_title."""

    def test_returns_none_when_value_is_none(self):
        """Should return None when value is None."""
        result = filter_title._filter_logic(None)
        assert result is None

    def test_returns_filter_expression_when_value_provided(self):
        """Should return ILIKE filter expression when value provided."""
        result = filter_title._filter_logic("test")
        assert result is not None

    def test_build_filter_returns_callable(self):
        """Should return callable dependency."""
        dependency = filter_title.build_filter()
        assert callable(dependency)


class TestFilterCategory:
    """Tests for filter_category."""

    def test_returns_none_when_value_is_none(self):
        """Should return None when value is None."""
        result = filter_category._filter_logic(None)
        assert result is None

    def test_returns_filter_expression_when_value_provided(self):
        """Should return ILIKE filter expression when value provided."""
        result = filter_category._filter_logic("Test Category")
        assert result is not None

    def test_build_filter_returns_callable(self):
        """Should return callable dependency."""
        dependency = filter_category.build_filter()
        assert callable(dependency)
