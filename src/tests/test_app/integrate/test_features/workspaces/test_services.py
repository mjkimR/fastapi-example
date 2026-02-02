"""
Integration app_tests for WorkspaceService.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.outbox.models import Outbox
from app.features.outbox.repos import OutboxRepository
from app.features.workspaces.enum import WorkspaceEventType
from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app.features.workspaces.services import WorkspaceService
from app_base.base.services.user_aware_hook import UserContextKwargs


class TestWorkspaceServiceIntegration:
    """Integration app_tests for WorkspaceService with a real database."""

    @pytest.fixture
    def repo(self) -> WorkspaceRepository:
        """Create a WorkspaceRepository instance."""
        return WorkspaceRepository()

    @pytest.fixture
    def outbox_repo(self) -> OutboxRepository:
        """Create an OutboxRepository instance."""
        return OutboxRepository()

    @pytest.fixture
    def service(self, repo: WorkspaceRepository, outbox_repo: OutboxRepository) -> WorkspaceService:
        """Create a WorkspaceService instance."""
        return WorkspaceService(repo=repo, outbox_repo=outbox_repo)

    @pytest.mark.asyncio
    async def test_create_workspace_and_creates_outbox_event(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        outbox_repo: OutboxRepository,
        regular_user,
    ):
        """Should create a new workspace and a corresponding outbox event."""
        workspace_data = WorkspaceCreate(name="Service Test Workspace")
        context: UserContextKwargs = {"user_id": regular_user.id}

        result = await service.create(session, obj_data=workspace_data, context=context)
        await session.commit()

        assert result is not None
        assert result.name == workspace_data.name

        # Verify outbox event
        outbox_event = await outbox_repo.get(session, where=[Outbox.aggregate_id == str(result.id)])
        assert outbox_event is not None
        assert outbox_event.event_type == WorkspaceEventType.CREATE
        assert outbox_event.payload["name"] == result.name

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
    async def test_update_workspace_and_creates_outbox_event(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        outbox_repo: OutboxRepository,
        single_workspace: Workspace,
        admin_user,
    ):
        """Should update a workspace and create a corresponding outbox event."""
        update_data = WorkspaceUpdate(name="Service Updated Workspace")
        context: UserContextKwargs = {"user_id": admin_user.id}

        result = await service.update(session, obj_id=single_workspace.id, obj_data=update_data, context=context)
        await session.commit()

        assert result is not None
        assert result.name == "Service Updated Workspace"

        # Verify outbox event
        outbox_event = await outbox_repo.get(session, where=[Outbox.aggregate_id == str(result.id)])
        assert outbox_event is not None
        assert outbox_event.event_type == WorkspaceEventType.UPDATE
        assert outbox_event.payload["name"] == "Service Updated Workspace"

    @pytest.mark.asyncio
    async def test_delete_workspace_and_creates_outbox_event(
        self,
        session: AsyncSession,
        service: WorkspaceService,
        outbox_repo: OutboxRepository,
        single_workspace: Workspace,
        regular_user,
    ):
        """Should delete a workspace and create a corresponding outbox event."""
        workspace_id = single_workspace.id
        workspace_name = single_workspace.name
        context: UserContextKwargs = {"user_id": regular_user.id}
        result = await service.delete(session, obj_id=workspace_id, context=context)
        await session.commit()

        assert result.success is True

        # Verify deletion
        deleted_workspace = await service.get(session, obj_id=workspace_id, context=context)
        assert deleted_workspace is None

        # Verify outbox event
        outbox_event = await outbox_repo.get(session, where=[Outbox.aggregate_id == str(workspace_id)])
        assert outbox_event is not None
        assert outbox_event.event_type == WorkspaceEventType.DELETE
        assert outbox_event.payload["name"] == workspace_name
