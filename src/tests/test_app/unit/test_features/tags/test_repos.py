from unittest.mock import MagicMock

import pytest

from app.features.tags.models import Tag
from app.features.tags.repos import TagRepository


class TestTagRepository:
    """Tests for TagRepository."""

    @pytest.fixture
    def tag_repo(self):
        """Create TagRepository instance."""
        return TagRepository()

    def test_model_is_tag(self, tag_repo):
        """Should have Tag as model."""
        assert tag_repo.model == Tag


class TestTagRepositoryGetOrCreateTags:
    """Tests for get_or_create_tags method."""

    @pytest.fixture
    def tag_repo(self):
        """Create TagRepository instance."""
        return TagRepository()

    @pytest.mark.asyncio
    async def test_returns_empty_list_for_empty_input(self, tag_repo, mock_async_session, sample_workspace_id):
        """Should return empty list for empty tag names."""
        result = await tag_repo.get_or_create_tags(mock_async_session, [], sample_workspace_id)

        assert result == []
        mock_async_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_existing_tags(self, tag_repo, mock_async_session, mock_tags, sample_workspace_id):
        """Should return existing tags without creating new ones."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_tags
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await tag_repo.get_or_create_tags(
            mock_async_session, ["python", "fastapi", "sqlalchemy"], sample_workspace_id
        )

        assert len(result) == 3
        mock_async_session.add_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_new_tags(self, tag_repo, mock_async_session, sample_workspace_id):
        """Should create new tags for names that don't exist."""
        # No existing tags
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await tag_repo.get_or_create_tags(mock_async_session, ["new-tag-1", "new-tag-2"], sample_workspace_id)

        assert len(result) == 2
        mock_async_session.add_all.assert_called_once()
        mock_async_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_mix_of_existing_and_new_tags(
        self, tag_repo, mock_async_session, mock_tag, sample_workspace_id
    ):
        """Should return both existing and newly created tags."""
        # One existing tag
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_tag]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        result = await tag_repo.get_or_create_tags(mock_async_session, [mock_tag.name, "new-tag"], sample_workspace_id)

        # Should have existing + new tag
        assert len(result) == 2
        mock_async_session.add_all.assert_called_once()
