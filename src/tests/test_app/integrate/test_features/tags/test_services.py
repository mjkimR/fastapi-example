"""
Integration app_tests for TagService.
Tests service layer operations with real database connections.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tags.models import Tag
from app.features.tags.repos import TagRepository
from app.features.tags.services import TagService
from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository
from app_base.base.services.nested_resource_hook import NestedResourceContextKwargs


class TestTagServiceIntegration:
    """Integration app_tests for TagService with real database."""

    @pytest.fixture
    def repo(self) -> TagRepository:
        """Create a TagRepository instance."""
        return TagRepository()

    @pytest.fixture
    def parent_repo(self) -> WorkspaceRepository:
        """Create a WorkspaceRepository instance."""
        return WorkspaceRepository()

    @pytest.fixture
    def service(self, repo: TagRepository, parent_repo: WorkspaceRepository) -> TagService:
        """Create a TagService instance."""
        return TagService(repo=repo, parent_repo=parent_repo)

    @pytest.mark.asyncio
    async def test_get_tag(self, session: AsyncSession, service: TagService, single_tag: Tag):
        """Should retrieve a tag through service."""
        context: NestedResourceContextKwargs = {"parent_id": single_tag.workspace_id}
        result = await service.get(session, obj_id=single_tag.id, context=context)

        assert result is not None
        assert result.id == single_tag.id
        assert result.name == single_tag.name

    @pytest.mark.asyncio
    async def test_get_multi_tags(
        self,
        session: AsyncSession,
        service: TagService,
        sample_tags: list[Tag],
        single_workspace: Workspace,
    ):
        """Should retrieve multiple tags through service."""
        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}
        result = await service.get_multi(session, offset=0, limit=10, context=context)

        assert result.total_count is not None
        assert result.total_count >= len(sample_tags)
        assert len(result.items) >= 1

    @pytest.mark.asyncio
    async def test_get_or_create_tags_new(
        self, session: AsyncSession, service: TagService, single_workspace: Workspace
    ):
        """Should create new tags through service."""
        tag_names = ["service_new_1", "service_new_2"]
        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}

        result = await service.get_or_create_tags(session, tag_names, context)

        assert len(result) == 2
        result_names = {tag.name for tag in result}
        assert result_names == set(tag_names)

    @pytest.mark.asyncio
    async def test_get_or_create_tags_existing(
        self, session: AsyncSession, service: TagService, single_workspace: Workspace
    ):
        """Should return existing tags through service."""
        existing_tag = Tag(name="service_existing", workspace_id=single_workspace.id)
        session.add(existing_tag)
        await session.flush()
        await session.refresh(existing_tag)

        tag_names = ["service_existing", "service_brand_new"]
        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}

        result = await service.get_or_create_tags(session, tag_names, context)

        assert len(result) == 2
        result_names = {tag.name for tag in result}
        assert "service_existing" in result_names
        assert "service_brand_new" in result_names

    @pytest.mark.asyncio
    async def test_get_or_create_tags_empty(
        self, session: AsyncSession, service: TagService, single_workspace: Workspace
    ):
        """Should handle empty tag list through service."""
        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}
        result = await service.get_or_create_tags(session, [], context)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_tag_not_found(self, session: AsyncSession, service: TagService, single_workspace: Workspace):
        """Should return None when tag not found."""
        non_existent_id = uuid.uuid4()
        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}
        result = await service.get(session, obj_id=non_existent_id, context=context)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_tags_with_filter(
        self, session: AsyncSession, service: TagService, single_workspace: Workspace
    ):
        """Should filter tags through service."""
        tag = Tag(name="filter_test_tag", workspace_id=single_workspace.id)
        session.add(tag)
        await session.flush()

        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}
        result = await service.get_multi(
            session,
            offset=0,
            limit=10,
            where=[Tag.name == "filter_test_tag"],
            context=context,
        )

        assert result.total_count is not None
        assert result.total_count >= 1
        assert any(t.name == "filter_test_tag" for t in result.items)

    @pytest.mark.asyncio
    async def test_get_multi_tags_with_pagination(
        self, session: AsyncSession, service: TagService, single_workspace: Workspace
    ):
        """Should paginate tags correctly through service."""
        for i in range(5):
            session.add(Tag(name=f"paginate_tag_{i}", workspace_id=single_workspace.id))
        await session.flush()

        context: NestedResourceContextKwargs = {"parent_id": single_workspace.id}
        result_page1 = await service.get_multi(session, offset=0, limit=2, context=context)
        result_page2 = await service.get_multi(session, offset=2, limit=2, context=context)

        assert result_page1.offset == 0
        assert result_page1.limit == 2
        assert len(result_page1.items) <= 2

        assert result_page2.offset == 2
        assert result_page2.limit == 2
