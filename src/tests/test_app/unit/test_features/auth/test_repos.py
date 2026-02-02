from unittest.mock import MagicMock

import pytest

from app.features.auth.models import User
from app.features.auth.repos import UserRepository


class TestUserRepository:
    """Tests for UserRepository."""

    @pytest.fixture
    def user_repo(self):
        """Create UserRepository instance."""
        return UserRepository()

    def test_model_is_user(self, user_repo):
        """Should have User as model."""
        assert user_repo.model == User

    @pytest.mark.asyncio
    async def test_get_by_email_returns_user_when_found(self, user_repo, mock_async_session, mock_user):
        """Should return user when found by email."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_async_session.execute.return_value = mock_result

        result = await user_repo.get_by_email(mock_async_session, "test@example.com")

        assert result == mock_user
        mock_async_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_email_returns_none_when_not_found(self, user_repo, mock_async_session):
        """Should return None when user not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result

        result = await user_repo.get_by_email(mock_async_session, "nonexistent@example.com")

        assert result is None
