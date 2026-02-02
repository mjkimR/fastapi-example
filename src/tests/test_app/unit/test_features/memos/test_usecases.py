from unittest.mock import AsyncMock, patch

import pytest

from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.features.memos.usecases.crud import (
    CreateMemoUseCase,
    DeleteMemoUseCase,
    GetMemoUseCase,
    GetMultiMemoUseCase,
    UpdateMemoUseCase,
)
from app_base.base.schemas.delete_resp import DeleteResponse
from app_base.base.schemas.paginated import PaginatedList


class TestGetMemoUseCase:
    """Tests for GetMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        service = AsyncMock()
        return GetMemoUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_calls_service_get(self, use_case, mock_memo, sample_memo_id, mock_user, mock_workspace):
        use_case.service.get.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app_base.base.usecases.crud.AsyncTransaction") as mock_tx:
            result = await use_case.execute(sample_memo_id, context=context)

        assert result is mock_memo
        use_case.service.get.assert_called_once_with(
            mock_tx.return_value.__aenter__.return_value,
            sample_memo_id,
            context=context,
        )


class TestGetMultiMemoUseCase:
    """Tests for GetMultiMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        service = AsyncMock()
        return GetMultiMemoUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_paginated_list(self, use_case, mock_memo, mock_user, mock_workspace):
        paginated = PaginatedList(items=[mock_memo], total_count=1, offset=0, limit=10)
        use_case.service.get_multi.return_value = paginated
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(offset=0, limit=10, context=context)

        assert result is paginated
        use_case.service.get_multi.assert_called_once()


class TestCreateMemoUseCase:
    """Tests for CreateMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        memo_service = AsyncMock()
        tag_service = AsyncMock()
        return CreateMemoUseCase(service=memo_service, tag_service=tag_service)

    @pytest.mark.asyncio
    async def test_execute_creates_memo_with_tags(self, use_case, mock_memo, mock_tags, mock_user, mock_workspace):
        use_case.tag_service.get_or_create_tags.return_value = mock_tags
        use_case.service.create.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}
        memo_data = MemoCreate(
            category="Test",
            title="Test Title",
            contents="Test Contents",
            tags=["python", "fastapi"],
        )

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(memo_data, context=context)

        use_case.tag_service.get_or_create_tags.assert_called_once()
        use_case.service.create.assert_called_once()
        assert result.tags == mock_tags

    @pytest.mark.asyncio
    async def test_execute_creates_memo_without_tags(self, use_case, mock_memo, mock_user, mock_workspace):
        use_case.service.create.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}
        memo_data = MemoCreate(
            category="Test",
            title="Test Title No Tags",
            contents="Test Contents No Tags",
            tags=[],
        )

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(memo_data, context=context)

        use_case.tag_service.get_or_create_tags.assert_not_called()
        use_case.service.create.assert_called_once()
        assert result is mock_memo


class TestUpdateMemoUseCase:
    """Tests for UpdateMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        memo_service = AsyncMock()
        tag_service = AsyncMock()
        return UpdateMemoUseCase(service=memo_service, tag_service=tag_service)

    @pytest.mark.asyncio
    async def test_execute_updates_memo_and_tags(
        self, use_case, mock_memo, mock_tags, sample_memo_id, mock_user, mock_workspace
    ):
        use_case.tag_service.get_or_create_tags.return_value = mock_tags
        use_case.service.update.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}
        update_data = MemoUpdate(title="Updated Title", tags=["new", "tags"])

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(sample_memo_id, update_data, context)

        use_case.tag_service.get_or_create_tags.assert_called_once()
        use_case.service.update.assert_called_once()
        assert result.tags == mock_tags

    @pytest.mark.asyncio
    async def test_execute_updates_memo_without_changing_tags(
        self, use_case, mock_memo, sample_memo_id, mock_user, mock_workspace
    ):
        use_case.service.update.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}
        update_data = MemoUpdate(title="Updated Title Only")

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            await use_case.execute(sample_memo_id, update_data, context)

        use_case.tag_service.get_or_create_tags.assert_not_called()
        use_case.service.update.assert_called_once()


class TestDeleteMemoUseCase:
    """Tests for DeleteMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        service = AsyncMock()
        return DeleteMemoUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_calls_service_delete(self, use_case, sample_memo_id, mock_user, mock_workspace):
        response = DeleteResponse(success=True, identity=sample_memo_id)
        use_case.service.delete.return_value = response
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app_base.base.usecases.crud.AsyncTransaction"):
            result = await use_case.execute(sample_memo_id, context=context)

        assert result is response
        use_case.service.delete.assert_called_once()
