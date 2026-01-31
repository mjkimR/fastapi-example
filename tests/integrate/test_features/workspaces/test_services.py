"""
Integration tests for WorkspaceService.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.services.user_aware_hook import UserContextKwargs
from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.services import WorkspaceService
from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app.features.workspaces.models import Workspace


class TestWorkspaceServiceIntegration:
    """Integration tests for WorkspaceService with a real database."""

    @pytest.fixture
    def repo(self) -> WorkspaceRepository:
        """Create a WorkspaceRepository instance."""
        return WorkspaceRepository()

    @pytest.fixture
    def service(self, repo: WorkspaceRepository) -> WorkspaceService:
        """Create a WorkspaceService instance."""
        return WorkspaceService(repo=repo)

    @pytest.mark.asyncio
    async def test_create_workspace(
        self, session: AsyncSession, service: WorkspaceService, regular_user
    ):
        """Should create a new workspace through the service."""
        workspace_data = WorkspaceCreate(name="Service Test Workspace")
        context: UserContextKwargs = {"user_id": regular_user.id}

        result = await service.create(session, obj_data=workspace_data, context=context)

        assert result is not None
        assert result.id is not None
        assert result.name == workspace_data.name
        assert result.created_by == regular_user.id

    @pytest.mark.asyncio
    async def test_get_workspace(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        single_workspace: Workspace,
        regular_user,
    ):
        """Should retrieve a workspace through the service."""
        context: UserContextKwargs = {"user_id": regular_user.id}
        result = await service.get(session, obj_id=single_workspace.id, context=context)

        assert result is not None
        assert result.id == single_workspace.id

    @pytest.mark.asyncio
    async def test_get_multi_workspaces(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        sample_workspaces: list[Workspace],
        regular_user,
    ):
        """Should retrieve multiple workspaces through the service."""
        context: UserContextKwargs = {"user_id": regular_user.id}
        result = await service.get_multi(session, offset=0, limit=10, context=context)

        assert result.total_count is not None
        assert result.total_count >= len(sample_workspaces)
        assert len(result.items) >= 1

    @pytest.mark.asyncio
    async def test_update_workspace(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        single_workspace: Workspace,
        admin_user,
    ):
        """Should update a workspace through the service."""
        update_data = WorkspaceUpdate(name="Service Updated Workspace")
        context: UserContextKwargs = {"user_id": admin_user.id}

        result = await service.update(
            session, obj_id=single_workspace.id, obj_data=update_data, context=context
        )

        assert result is not None
        assert result.name == "Service Updated Workspace"
        assert result.updated_by == admin_user.id

    @pytest.mark.asyncio
    async def test_delete_workspace(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        single_workspace: Workspace,
        regular_user,
    ):
        """Should delete a workspace through the service."""
        context: UserContextKwargs = {"user_id": regular_user.id}
        result = await service.delete(
            session, obj_id=single_workspace.id, context=context
        )

        assert result.success is True

        # Verify deletion
        deleted_workspace = await service.get(
            session, obj_id=single_workspace.id, context=context
        )
        assert deleted_workspace is None
