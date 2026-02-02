from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.features.workspaces.enum import WorkspaceEventType
from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app.features.workspaces.services import WorkspaceService
from app_base.base.services.user_aware_hook import UserContextKwargs


class TestWorkspaceServiceOutboxHooks:
    """Unit app_tests for the NotificationOutboxHook mixin in WorkspaceService."""

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        # Ensure model_name is a regular mock, not an async one
        repo.model_name = MagicMock(return_value="workspace")
        return repo

    @pytest.fixture
    def mock_outbox_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo, mock_outbox_repo) -> WorkspaceService:
        return WorkspaceService(repo=mock_repo, outbox_repo=mock_outbox_repo)

    @pytest.mark.asyncio
    async def test_create_calls_outbox_repo(
        self,
        service: WorkspaceService,
        mock_outbox_repo,
        mock_async_session,
        mock_user,
        sample_workspace_id,
    ):
        """Should call outbox_repo.create after a successful workspace creation."""
        created_mock = MagicMock()
        created_mock.id = sample_workspace_id
        created_mock.name = "Test Workspace"
        cast(AsyncMock, service.repo.create).return_value = created_mock
        # Mock for UniqueConstraintHooksMixin
        cast(AsyncMock, service.repo.exists).return_value = False
        workspace_data = WorkspaceCreate(name="Test Workspace")
        context: UserContextKwargs = {"user_id": mock_user.id}

        await service.create(mock_async_session, workspace_data, context)

        mock_outbox_repo.create.assert_called_once()
        call_args = mock_outbox_repo.create.call_args.kwargs
        assert call_args["obj_in"].aggregate_id == str(sample_workspace_id)
        assert call_args["obj_in"].event_type == WorkspaceEventType.CREATE
        assert call_args["obj_in"].payload["name"] == "Test Workspace"

    @pytest.mark.asyncio
    async def test_update_calls_outbox_repo(
        self,
        service: WorkspaceService,
        mock_outbox_repo,
        mock_async_session,
        mock_user,
        sample_workspace_id,
    ):
        """Should call outbox_repo.create after a successful workspace update."""
        updated_mock = MagicMock()
        updated_mock.id = sample_workspace_id
        updated_mock.name = "Updated Name"
        cast(AsyncMock, service.repo.update_by_pk).return_value = updated_mock
        # Mock for UniqueConstraintHooksMixin
        cast(AsyncMock, service.repo.exists).return_value = False
        update_data = WorkspaceUpdate(name="Updated Name")
        context: UserContextKwargs = {"user_id": mock_user.id}

        await service.update(mock_async_session, sample_workspace_id, update_data, context)

        mock_outbox_repo.create.assert_called_once()
        call_args = mock_outbox_repo.create.call_args.kwargs
        assert call_args["obj_in"].aggregate_id == str(sample_workspace_id)
        assert call_args["obj_in"].event_type == WorkspaceEventType.UPDATE
        assert call_args["obj_in"].payload["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete_calls_outbox_repo(
        self,
        service: WorkspaceService,
        mock_outbox_repo,
        mock_async_session,
        mock_user,
        sample_workspace_id,
    ):
        """Should call outbox_repo.create after a successful workspace deletion."""
        deleted_mock = MagicMock()
        deleted_mock.id = sample_workspace_id
        deleted_mock.name = "Deleted Workspace"
        cast(AsyncMock, service.repo.get_by_pk).return_value = deleted_mock
        cast(AsyncMock, service.repo.delete_by_pk).return_value = True
        context: UserContextKwargs = {"user_id": mock_user.id}

        await service.delete(mock_async_session, sample_workspace_id, context)

        mock_outbox_repo.create.assert_called_once()
        call_args = mock_outbox_repo.create.call_args.kwargs
        assert call_args["obj_in"].aggregate_id == str(sample_workspace_id)
        assert call_args["obj_in"].event_type == WorkspaceEventType.DELETE
        assert call_args["obj_in"].payload["name"] == "Deleted Workspace"
