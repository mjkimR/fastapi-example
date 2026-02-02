from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.features.memos.enum import MemoEventType
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.features.memos.services import MemoContextKwargs, MemoService


class TestMemoServiceOutboxHooks:
    """Unit app_tests for the NotificationOutboxHook mixin in MemoService."""

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock()
        # Ensure model_name is a regular mock, not an async one
        repo.model_name = MagicMock(return_value="memo")
        return repo

    @pytest.fixture
    def mock_parent_repo(self):
        return AsyncMock()

    @pytest.fixture
    def mock_outbox_repo(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo, mock_parent_repo, mock_outbox_repo) -> MemoService:
        return MemoService(
            repo=mock_repo,
            parent_repo=mock_parent_repo,
            outbox_repo=mock_outbox_repo,
        )

    @pytest.mark.asyncio
    async def test_create_calls_outbox_repo(
        self,
        service: MemoService,
        mock_outbox_repo,
        mock_async_session,
        mock_memo,
        sample_memo_id,
    ):
        """Should call outbox_repo.create after a successful memo creation."""
        created_mock = MagicMock()
        created_mock.id = sample_memo_id
        created_mock.title = "Test"
        created_mock.workspace_id = mock_memo.workspace_id
        cast(AsyncMock, service.repo.create).return_value = created_mock
        # Mocks for hooks
        cast(AsyncMock, service.repo.exists).return_value = False
        cast(AsyncMock, service.parent_repo.exists).return_value = True

        memo_data = MemoCreate(category="Test Category", title="Test", contents="Test", tags=[])
        context: MemoContextKwargs = {
            "parent_id": mock_memo.workspace_id,
            "user_id": mock_memo.created_by,
        }

        await service.create(mock_async_session, memo_data, context)

        mock_outbox_repo.create.assert_called_once()
        call_args = mock_outbox_repo.create.call_args.kwargs
        assert call_args["obj_in"].aggregate_id == str(sample_memo_id)
        assert call_args["obj_in"].event_type == MemoEventType.CREATE
        assert call_args["obj_in"].payload["title"] == "Test"

    @pytest.mark.asyncio
    async def test_update_calls_outbox_repo(
        self,
        service: MemoService,
        mock_outbox_repo,
        mock_async_session,
        mock_memo,
        sample_memo_id,
    ):
        """Should call outbox_repo.create after a successful memo update."""
        # Mocks for hooks
        cast(AsyncMock, service.repo.exists).return_value = False
        cast(AsyncMock, service.parent_repo.exists).return_value = True
        cast(AsyncMock, service.repo.get_by_pk).return_value = mock_memo

        updated_mock = MagicMock()
        updated_mock.id = sample_memo_id
        updated_mock.title = "Updated Title"
        updated_mock.workspace_id = mock_memo.workspace_id
        cast(AsyncMock, service.repo.update_by_pk).return_value = updated_mock

        update_data = MemoUpdate(title="Updated Title")
        context: MemoContextKwargs = {
            "parent_id": mock_memo.workspace_id,
            "user_id": mock_memo.created_by,
        }

        await service.update(mock_async_session, sample_memo_id, update_data, context)

        mock_outbox_repo.create.assert_called_once()
        call_args = mock_outbox_repo.create.call_args.kwargs
        assert call_args["obj_in"].aggregate_id == str(sample_memo_id)
        assert call_args["obj_in"].event_type == MemoEventType.UPDATE
        assert call_args["obj_in"].payload["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_calls_outbox_repo(
        self,
        service: MemoService,
        mock_outbox_repo,
        mock_async_session,
        mock_memo,
        sample_memo_id,
    ):
        """Should call outbox_repo.create after a successful memo deletion."""
        deleted_mock = MagicMock()
        deleted_mock.id = sample_memo_id
        deleted_mock.title = "Deleted Memo"
        deleted_mock.workspace_id = mock_memo.workspace_id
        cast(AsyncMock, service.repo.get_by_pk).return_value = deleted_mock
        cast(AsyncMock, service.parent_repo.exists).return_value = True
        cast(AsyncMock, service.repo.delete_by_pk).return_value = MagicMock(success=True)

        context: MemoContextKwargs = {
            "parent_id": mock_memo.workspace_id,
            "user_id": mock_memo.created_by,
        }

        await service.delete(mock_async_session, sample_memo_id, context)

        mock_outbox_repo.create.assert_called_once()
        call_args = mock_outbox_repo.create.call_args.kwargs
        assert call_args["obj_in"].aggregate_id == str(sample_memo_id)
        assert call_args["obj_in"].event_type == MemoEventType.DELETE
        assert call_args["obj_in"].payload["title"] == "Deleted Memo"
