from unittest.mock import AsyncMock, patch

import pytest

from app.features.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app.features.workspaces.usecases.crud import (
    CreateWorkspaceUseCase,
    DeleteWorkspaceUseCase,
    GetMultiWorkspaceUseCase,
    GetWorkspaceUseCase,
    UpdateWorkspaceUseCase,
)
from app_base.base.schemas.paginated import PaginatedList
from app_base.base.services.user_aware_hook import UserContextKwargs


class TestGetWorkspaceUseCase:
    """Tests for GetWorkspaceUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return GetWorkspaceUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_workspace(self, use_case, mock_workspace):
        """Should return workspace when found."""
        use_case.service.get.return_value = mock_workspace

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(mock_workspace.id)

        assert result == mock_workspace
        use_case.service.get.assert_called_once()


class TestGetMultiWorkspaceUseCase:
    """Tests for GetMultiWorkspaceUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return GetMultiWorkspaceUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_paginated_workspaces(self, use_case, mock_workspace):
        """Should return paginated list of workspaces."""
        paginated = PaginatedList(items=[mock_workspace], total_count=1, offset=0, limit=10)
        use_case.service.get_multi.return_value = paginated

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(offset=0, limit=10)

        assert result == paginated
        use_case.service.get_multi.assert_called_once()


class TestCreateWorkspaceUseCase:
    """Tests for CreateWorkspaceUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        workspace_service = AsyncMock()
        return CreateWorkspaceUseCase(service=workspace_service)

    @pytest.mark.asyncio
    async def test_execute_creates_workspace(self, use_case, mock_workspace, mock_user):
        """Should create workspace via service."""
        use_case.service.create.return_value = mock_workspace
        workspace_data = WorkspaceCreate(name="Test Workspace")
        context: UserContextKwargs = {"user_id": mock_user.id}
        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(workspace_data, context=context)

        assert result == mock_workspace
        use_case.service.create.assert_called_once()


class TestUpdateWorkspaceUseCase:
    """Tests for UpdateWorkspaceUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return UpdateWorkspaceUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_updates_workspace(self, use_case, mock_workspace):
        """Should update workspace via service."""
        use_case.service.update.return_value = mock_workspace
        update_data = WorkspaceUpdate(name="Updated Workspace")

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(mock_workspace.id, update_data)

        assert result == mock_workspace
        use_case.service.update.assert_called_once()


class TestDeleteWorkspaceUseCase:
    """Tests for DeleteWorkspaceUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return DeleteWorkspaceUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_deletes_workspace(self, use_case, mock_workspace):
        """Should delete workspace via service."""
        use_case.service.delete.return_value = "DeleteResponse"

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(mock_workspace.id)

        assert result == "DeleteResponse"
        use_case.service.delete.assert_called_once()
