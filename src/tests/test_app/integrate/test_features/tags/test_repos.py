"""
Integration app_tests for TagRepository.
Tests CRUD operations with real database connections.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tags.models import Tag
from app.features.tags.repos import TagRepository
from app.features.workspaces.models import Workspace


class TestTagRepositoryIntegration:
    """Integration app_tests for TagRepository with real database."""

    @pytest.fixture
    def repo(self) -> TagRepository:
        """Create a TagRepository instance."""
        return TagRepository()

    @pytest.mark.asyncio
    async def test_create_tag(self, session: AsyncSession, repo: TagRepository, single_workspace: Workspace):
        """Should create a new tag in the database."""
        tag = Tag(name="python", workspace_id=single_workspace.id)
        session.add(tag)
        await session.flush()
        await session.refresh(tag)

        assert tag.id is not None
        assert tag.name == "python"
        assert tag.workspace_id == single_workspace.id

    @pytest.mark.asyncio
    async def test_get_tag_by_pk(self, session: AsyncSession, repo: TagRepository, single_tag: Tag):
        """Should retrieve a tag by primary key."""
        result = await repo.get_by_pk(session, pk=single_tag.id)

        assert result is not None
        assert result.id == single_tag.id
        assert result.name == single_tag.name

    @pytest.mark.asyncio
    async def test_get_tag_by_pk_not_found(self, session: AsyncSession, repo: TagRepository):
        """Should return None when tag not found."""
        non_existent_id = uuid.uuid4()

        result = await repo.get_by_pk(session, pk=non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_tags(self, session: AsyncSession, repo: TagRepository, sample_tags: list[Tag]):
        """Should retrieve multiple tags with pagination."""
        result = await repo.get_multi(session, offset=0, limit=10)

        assert result.total_count is not None
        assert result.total_count >= len(sample_tags)
        assert len(result.items) <= 10

    @pytest.mark.asyncio
    async def test_get_or_create_tags_new_tags(
        self, session: AsyncSession, repo: TagRepository, single_workspace: Workspace
    ):
        """Should create new tags when they don't exist."""
        tag_names = ["new_tag_1", "new_tag_2", "new_tag_3"]
        workspace_id = single_workspace.id

        result = await repo.get_or_create_tags(session, tag_names, workspace_id)

        assert len(result) == 3
        result_names = {tag.name for tag in result}
        assert result_names == set(tag_names)
        for tag in result:
            assert tag.workspace_id == workspace_id

    @pytest.mark.asyncio
    async def test_get_or_create_tags_existing_tags(
        self, session: AsyncSession, repo: TagRepository, single_workspace: Workspace
    ):
        """Should return existing tags without creating duplicates."""
        workspace_id = single_workspace.id
        existing_tag = Tag(name="existing_tag", workspace_id=workspace_id)
        session.add(existing_tag)
        await session.flush()
        await session.refresh(existing_tag)

        tag_names = ["existing_tag", "another_new_tag"]

        result = await repo.get_or_create_tags(session, tag_names, workspace_id)

        assert len(result) == 2
        result_names = {tag.name for tag in result}
        assert "existing_tag" in result_names
        assert "another_new_tag" in result_names

    @pytest.mark.asyncio
    async def test_get_or_create_tags_mixed(
        self, session: AsyncSession, repo: TagRepository, single_workspace: Workspace
    ):
        """Should handle mix of existing and new tags."""
        workspace_id = single_workspace.id
        existing_tags = [
            Tag(name="mix_existing_1", workspace_id=workspace_id),
            Tag(name="mix_existing_2", workspace_id=workspace_id),
        ]
        session.add_all(existing_tags)
        await session.flush()

        tag_names = ["mix_existing_1", "mix_new_1", "mix_existing_2", "mix_new_2"]

        result = await repo.get_or_create_tags(session, tag_names, workspace_id)

        assert len(result) == 4
        result_names = {tag.name for tag in result}
        assert result_names == set(tag_names)

    @pytest.mark.asyncio
    async def test_get_or_create_tags_empty_list(
        self, session: AsyncSession, repo: TagRepository, single_workspace: Workspace
    ):
        """Should return empty list for empty input."""
        result = await repo.get_or_create_tags(session, [], single_workspace.id)
        assert result == []

    @pytest.mark.asyncio
    async def test_delete_tag_by_pk(self, session: AsyncSession, repo: TagRepository, single_tag: Tag):
        """Should delete a tag from the database."""
        tag_id = single_tag.id
        result = await repo.delete_by_pk(session, pk=tag_id)
        assert result is True
        deleted_tag = await repo.get_by_pk(session, pk=tag_id)
        assert deleted_tag is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tag(self, session: AsyncSession, repo: TagRepository):
        """Should return False when deleting non-existent tag."""
        non_existent_id = uuid.uuid4()
        result = await repo.delete_by_pk(session, pk=non_existent_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_tag(self, session: AsyncSession, repo: TagRepository, single_tag: Tag):
        """Should check if tag exists."""
        result = await repo.exists(session, where=Tag.id == single_tag.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_tag_by_name(self, session: AsyncSession, repo: TagRepository, single_tag: Tag):
        """Should check if tag exists by name in the same workspace."""
        result = await repo.exists(
            session,
            where=(Tag.name == single_tag.name) & (Tag.workspace_id == single_tag.workspace_id),
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_tag_not_found(self, session: AsyncSession, repo: TagRepository):
        """Should return False when tag does not exist."""
        non_existent_id = uuid.uuid4()
        result = await repo.exists(session, where=Tag.id == non_existent_id)
        assert result is False
