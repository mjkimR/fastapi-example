import uuid
from typing import cast
from unittest.mock import AsyncMock

import pytest

from app.features.outbox.models import EventStatus, Outbox
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.schemas import OutboxCreate
from app.features.outbox.services import OutboxService


class TestOutboxService:
    """Unit app_tests for OutboxService."""

    @pytest.fixture
    def mock_outbox_repo(self) -> OutboxRepository:
        """Create a mock OutboxRepository instance."""
        return AsyncMock(spec=OutboxRepository)

    @pytest.fixture
    def outbox_service(self, mock_outbox_repo: OutboxRepository) -> OutboxService:
        """Create an OutboxService instance with a mocked repository."""
        return OutboxService(repo=mock_outbox_repo)

    @pytest.mark.asyncio
    async def test_add_event(
        self,
        outbox_service: OutboxService,
        mock_outbox_repo: OutboxRepository,
        mock_async_session,
    ):
        """Should call repo.create with the correct OutboxCreate data."""
        event_data = OutboxCreate(
            aggregate_type="test_type",
            aggregate_id=str(uuid.uuid4()),
            event_type="TEST_EVENT",
            payload={"key": "value"},
        )
        repo_method = cast(AsyncMock, mock_outbox_repo.create)
        repo_method.return_value = Outbox(
            id=uuid.uuid4(),
            **event_data.model_dump(),
            status=EventStatus.PENDING,
            retry_count=0,
        )

        result = await outbox_service.add_event(mock_async_session, event_data)

        repo_method.assert_called_once_with(mock_async_session, obj_in=event_data)
        assert result.event_type == "TEST_EVENT"

    @pytest.mark.asyncio
    async def test_update_event_status_completed(
        self,
        outbox_service: OutboxService,
        mock_outbox_repo: OutboxRepository,
        mock_async_session,
    ):
        """Should update event status to COMPLETED and set processed_at."""
        event_id = uuid.uuid4()
        repo_method = cast(AsyncMock, mock_outbox_repo.update_by_pk)
        repo_method.return_value = Outbox(
            id=event_id,
            aggregate_type="test",
            aggregate_id=str(uuid.uuid4()),
            event_type="TEST_EVENT",
            payload={},
            status=EventStatus.COMPLETED,
        )

        result = await outbox_service.update_event_status(mock_async_session, event_id, EventStatus.COMPLETED)

        repo_method.assert_called_once()
        call_kwargs = repo_method.call_args.kwargs
        assert call_kwargs["pk"] == event_id
        assert call_kwargs["obj_in"].status == EventStatus.COMPLETED
        assert call_kwargs["obj_in"].processed_at is not None
        assert result is not None
        assert result.status == EventStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_update_event_status_failed(
        self,
        outbox_service: OutboxService,
        mock_outbox_repo: OutboxRepository,
        mock_async_session,
    ):
        """Should update event status to FAILED and increment retry_count."""
        event_id = uuid.uuid4()
        repo_method = cast(AsyncMock, mock_outbox_repo.update_by_pk)
        repo_method.return_value = Outbox(
            id=event_id,
            aggregate_type="test",
            aggregate_id=str(uuid.uuid4()),
            event_type="TEST_EVENT",
            payload={},
            status=EventStatus.FAILED,
            retry_count=1,
        )

        result = await outbox_service.update_event_status(
            mock_async_session, event_id, EventStatus.FAILED, retry_count=1
        )

        repo_method.assert_called_once()
        call_kwargs = repo_method.call_args.kwargs
        assert call_kwargs["pk"] == event_id
        assert call_kwargs["obj_in"].status == EventStatus.FAILED
        assert call_kwargs["obj_in"].retry_count == 1
        assert result is not None
        assert result.status == EventStatus.FAILED
