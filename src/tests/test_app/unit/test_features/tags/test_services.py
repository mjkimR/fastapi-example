from unittest.mock import AsyncMock

import pytest

from app.features.tags.services import TagService


class TestTagService:
    """Tests for TagService."""

    @pytest.fixture
    def tag_service(self):
        """Create TagService with mocked repository."""
        repo = AsyncMock()
        parent_repo = AsyncMock()
        service = TagService(repo=repo, parent_repo=parent_repo)
        return service

    @pytest.mark.asyncio
    async def test_get_or_create_tags_delegates_to_repo(
        self, tag_service, mock_async_session, mock_tags, sample_workspace_id
    ):
        """Should delegate to repository."""
        tag_service.repo.get_or_create_tags.return_value = mock_tags
        tag_names = ["python", "fastapi"]
        context = {"parent_id": sample_workspace_id}

        result = await tag_service.get_or_create_tags(mock_async_session, tag_names, context)

        assert result == mock_tags
        tag_service.repo.get_or_create_tags.assert_called_once_with(
            mock_async_session, tag_names, workspace_id=sample_workspace_id
        )

    @pytest.mark.asyncio
    async def test_get_or_create_tags_with_empty_list(self, tag_service, mock_async_session, sample_workspace_id):
        """Should handle empty tag list."""
        tag_service.repo.get_or_create_tags.return_value = []
        context = {"parent_id": sample_workspace_id}

        result = await tag_service.get_or_create_tags(mock_async_session, [], context)

        assert result == []
        tag_service.repo.get_or_create_tags.assert_called_once_with(
            mock_async_session, [], workspace_id=sample_workspace_id
        )
