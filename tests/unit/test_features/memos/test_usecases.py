from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.features.memos.enum import MEMO_RES_NAME, MemoEventType
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.features.memos.usecases.crud import (
    GetMemoUseCase,
    GetMultiMemoUseCase,
    CreateMemoUseCase,
    UpdateMemoUseCase,
    DeleteMemoUseCase,
)
from app.base.schemas.paginated import PaginatedList
from tests.unit.fixtures.data import mock_workspace


class TestGetMemoUseCase:
    """Tests for GetMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return GetMemoUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_memo_when_found(
        self, use_case, mock_memo, sample_memo_id, mock_user, mock_workspace
    ):
        """Should return memo when found."""
        use_case.service.get.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app.base.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(sample_memo_id, context=context)

        assert result == mock_memo
        use_case.service.get.assert_called_with(
            mock_tx.return_value.__aenter__.return_value,
            sample_memo_id,
            context=context,
        )

    @pytest.mark.asyncio
    async def test_execute_returns_none_when_not_found(
        self, use_case, sample_memo_id, mock_user, mock_workspace
    ):
        """Should return None when memo not found."""
        use_case.service.get.return_value = None
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app.base.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(sample_memo_id, context=context)

        assert result is None


class TestGetMultiMemoUseCase:
    """Tests for GetMultiMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return GetMultiMemoUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_paginated_list(
        self, use_case, mock_memo, mock_user, mock_workspace
    ):
        """Should return paginated list of memos."""
        paginated = PaginatedList(items=[mock_memo], total_count=1, offset=0, limit=10)
        use_case.service.get_multi.return_value = paginated
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(offset=0, limit=10, context=context)

        assert result == paginated
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_execute_with_filters(
        self, use_case, mock_memo, mock_user, mock_workspace
    ):
        """Should pass filters to service."""
        paginated = PaginatedList(items=[mock_memo], total_count=1, offset=0, limit=10)
        use_case.service.get_multi.return_value = paginated
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        mock_where = MagicMock()
        mock_order_by = MagicMock()

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(
                offset=0,
                limit=10,
                where=mock_where,
                order_by=mock_order_by,
                context=context,
            )

        assert result == paginated


class TestCreateMemoUseCase:
    """Tests for CreateMemoUseCase."""

    @pytest.fixture
    def mock_outbox_service(self) -> AsyncMock:
        """Create a mock OutboxService instance."""
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_outbox_service: AsyncMock):
        """Create use case with mocked services."""
        memo_service = AsyncMock()
        tag_service = AsyncMock()
        return CreateMemoUseCase(
            memo_service=memo_service,
            tag_service=tag_service,
            outbox_service=mock_outbox_service,
        )

    @pytest.mark.asyncio
    async def test_execute_creates_memo_with_tags(
        self,
        use_case,
        mock_memo,
        mock_tags,
        mock_user,
        mock_workspace,
        mock_outbox_service: AsyncMock,
    ):
        """Should create memo, associate tags, and add outbox event."""
        use_case.tag_service.get_or_create_tags.return_value = mock_tags
        use_case.memo_service.create.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        memo_data = MemoCreate(
            category="Test",
            title="Test Title",
            contents="Test Contents",
            tags=["python", "fastapi"],
        )

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_session = AsyncMock()
            mock_tx.return_value.__aenter__.return_value = mock_session
            result = await use_case.execute(memo_data, context=context)

        use_case.tag_service.get_or_create_tags.assert_called_once_with(
            mock_session, memo_data.tags, context
        )
        use_case.memo_service.create.assert_called_once()

        # Assert outbox_service.add_event was called
        mock_outbox_service.add_event.assert_called_once()
        call_args = mock_outbox_service.add_event.call_args[0]
        assert call_args[0] == mock_session
        assert call_args[1].aggregate_type == MEMO_RES_NAME
        assert call_args[1].event_type == MemoEventType.CREATE
        assert call_args[1].payload["id"] == str(mock_memo.id)
        assert call_args[1].payload["user_id"] == str(mock_user.id)
        assert call_args[1].payload["title"] == mock_memo.title

        assert result == mock_memo

    @pytest.mark.asyncio
    async def test_execute_creates_memo_without_tags(
        self,
        use_case,
        mock_memo,
        mock_user,
        mock_workspace,
        mock_outbox_service: AsyncMock,
    ):
        """Should create memo without tags and add outbox event."""
        use_case.tag_service.get_or_create_tags.return_value = []
        use_case.memo_service.create.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        memo_data = MemoCreate(
            category="Test",
            title="Test Title No Tags",
            contents="Test Contents No Tags",
            tags=[],
        )

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_session = AsyncMock()
            mock_tx.return_value.__aenter__.return_value = mock_session
            result = await use_case.execute(memo_data, context=context)

        use_case.tag_service.get_or_create_tags.assert_called_once_with(
            mock_session, memo_data.tags, context
        )
        use_case.memo_service.create.assert_called_once()

        # Assert outbox_service.add_event was called
        mock_outbox_service.add_event.assert_called_once()
        call_args = mock_outbox_service.add_event.call_args[0]
        assert call_args[0] == mock_session
        assert call_args[1].aggregate_type == MEMO_RES_NAME
        assert call_args[1].event_type == MemoEventType.CREATE
        assert call_args[1].payload["id"] == str(mock_memo.id)
        assert call_args[1].payload["user_id"] == str(mock_user.id)
        assert (
            call_args[1].payload["title"] == mock_memo.title
        )  # Verify title is passed

        assert result == mock_memo


class TestUpdateMemoUseCase:
    """Tests for UpdateMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked services."""
        memo_service = AsyncMock()
        tag_service = AsyncMock()
        return UpdateMemoUseCase(memo_service=memo_service, tag_service=tag_service)

    @pytest.mark.asyncio
    async def test_execute_returns_none_when_memo_not_found(
        self, use_case, sample_memo_id, mock_user, mock_workspace
    ):
        """Should return None when memo not found."""
        use_case.memo_service.get.return_value = None
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        update_data = MemoUpdate(title="Updated Title")

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_session = AsyncMock()
            mock_tx.return_value.__aenter__.return_value = mock_session
            result = await use_case.execute(
                sample_memo_id, update_data, context=context
            )

        assert result is None

    @pytest.mark.asyncio
    async def test_execute_updates_memo_with_tags(
        self, use_case, mock_memo, mock_tags, sample_memo_id, mock_user, mock_workspace
    ):
        """Should update memo and tags."""
        use_case.memo_service.get.return_value = mock_memo
        use_case.tag_service.get_or_create_tags.return_value = mock_tags
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        update_data = MemoUpdate(title="Updated Title", tags=["python", "fastapi"])

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_session = AsyncMock()
            mock_tx.return_value.__aenter__.return_value = mock_session
            result = await use_case.execute(
                sample_memo_id, update_data, context=context
            )

        use_case.tag_service.get_or_create_tags.assert_called_once_with(
            mock_session, update_data.tags, context
        )
        assert result == mock_memo

    @pytest.mark.asyncio
    async def test_execute_updates_memo_without_tags(
        self, use_case, mock_memo, sample_memo_id, mock_user, mock_workspace
    ):
        """Should update memo without changing tags when tags is None."""
        use_case.memo_service.get.return_value = mock_memo
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        update_data = MemoUpdate(title="Updated Title")  # tags is None

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_session = AsyncMock()
            mock_tx.return_value.__aenter__.return_value = mock_session
            result = await use_case.execute(
                sample_memo_id, update_data, context=context
            )

        use_case.tag_service.get_or_create_tags.assert_not_called()
        assert result == mock_memo


class TestDeleteMemoUseCase:
    """Tests for DeleteMemoUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return DeleteMemoUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_true_when_deleted(
        self, use_case, sample_memo_id, mock_user, mock_workspace
    ):
        """Should return True when memo deleted."""
        use_case.service.delete.return_value = True
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(sample_memo_id, context=context)

        assert result is True

    @pytest.mark.asyncio
    async def test_execute_returns_false_when_not_found(
        self, use_case, sample_memo_id, mock_user, mock_workspace
    ):
        """Should return False when memo not found."""
        use_case.service.delete.return_value = False
        context = {"parent_id": mock_workspace.id, "user_id": mock_user.id}

        with patch("app.features.memos.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(sample_memo_id, context=context)

        assert result is False
