"""
Integration app_tests for WorkspaceRepository.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate


class TestWorkspaceRepositoryIntegration:
    """Integration app_tests for WorkspaceRepository with a real database."""

    @pytest.fixture
    def repo(self) -> WorkspaceRepository:
        """Create a WorkspaceRepository instance."""
        return WorkspaceRepository()

    @pytest.mark.asyncio
    async def test_create_workspace(self, session: AsyncSession, repo: WorkspaceRepository, regular_user):
        """Should create a new workspace in the database."""
        workspace_data = WorkspaceCreate(name="Test Workspace")

        result = await repo.create(
            session,
            obj_in=workspace_data,
            created_by=regular_user.id,
            updated_by=regular_user.id,
        )

        assert result is not None
        assert result.id is not None
        assert result.name == workspace_data.name
        assert result.created_by == regular_user.id

    @pytest.mark.asyncio
    async def test_get_workspace_by_pk(
        self,
        session: AsyncSession,
        repo: WorkspaceRepository,
        single_workspace: Workspace,
    ):
        """Should retrieve a workspace by primary key."""
        result = await repo.get_by_pk(session, pk=single_workspace.id)

        assert result is not None
        assert result.id == single_workspace.id
        assert result.name == single_workspace.name

    @pytest.mark.asyncio
    async def test_get_workspace_by_pk_not_found(self, session: AsyncSession, repo: WorkspaceRepository):
        """Should return None when workspace not found."""
        non_existent_id = uuid.uuid4()
        result = await repo.get_by_pk(session, pk=non_existent_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_workspaces(
        self,
        session: AsyncSession,
        repo: WorkspaceRepository,
        sample_workspaces: list[Workspace],
    ):
        """Should retrieve multiple workspaces with pagination."""
        result = await repo.get_multi(session, offset=0, limit=10)

        assert result.total_count is not None
        assert result.total_count >= len(sample_workspaces)
        assert len(result.items) <= 10

    @pytest.mark.asyncio
    async def test_update_workspace_by_pk(
        self,
        session: AsyncSession,
        repo: WorkspaceRepository,
        single_workspace: Workspace,
        admin_user,
    ):
        """Should update an existing workspace."""
        update_data = WorkspaceUpdate(name="Updated Workspace Name")

        result = await repo.update_by_pk(
            session,
            pk=single_workspace.id,
            obj_in=update_data,
            updated_by=admin_user.id,
        )

        assert result is not None
        assert result.name == "Updated Workspace Name"
        assert result.updated_by == admin_user.id

    @pytest.mark.asyncio
    async def test_delete_workspace_by_pk(
        self,
        session: AsyncSession,
        repo: WorkspaceRepository,
        single_workspace: Workspace,
    ):
        """Should delete a workspace from the database."""
        workspace_id = single_workspace.id
        result = await repo.delete_by_pk(session, pk=workspace_id)
        assert result is True

        deleted_workspace = await repo.get_by_pk(session, pk=workspace_id)
        assert deleted_workspace is None
