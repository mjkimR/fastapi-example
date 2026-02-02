import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.features.outbox.models import EventStatus, Outbox
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.schemas import OutboxCreate, OutboxUpdate


class TestOutboxRepository:
    """Unit app_tests for OutboxRepository."""

    @pytest.fixture
    def outbox_repo(self):
        """Create OutboxRepository instance."""
        return OutboxRepository()

    @pytest.mark.asyncio
    async def test_model_is_outbox(self, outbox_repo):
        """Should have Outbox as model."""
        assert outbox_repo.model == Outbox

    @pytest.mark.asyncio
    async def test_get_and_lock_pending_events_returns_events(self, outbox_repo, mock_async_session, mock_memo):
        """Should return pending events and apply for_update."""
        # Mocking an Outbox instance for pending events
        mock_outbox_event = Outbox(
            id=uuid.uuid4(),
            aggregate_type="memo",
            aggregate_id=str(mock_memo.id),
            event_type="MEMO_CREATED",
            payload={"memo_id": str(mock_memo.id)},
            status=EventStatus.PENDING,
            retry_count=0,
        )

        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_outbox_event]
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        events = await outbox_repo.get_and_lock_pending_events(mock_async_session, limit=1)

        assert len(events) == 1
        assert events[0].id == mock_outbox_event.id
        assert events[0].status == EventStatus.PENDING
        mock_async_session.execute.assert_called_once()
        # Verify the query includes with_for_update by checking the compiled SQL
        call_args = mock_async_session.execute.call_args[0][0]
        assert "FOR UPDATE" in str(call_args.compile(compile_kwargs={"literal_binds": True}))

    @pytest.mark.asyncio
    async def test_get_and_lock_pending_events_returns_empty_list_if_none(self, outbox_repo, mock_async_session):
        """Should return an empty list if no pending events."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_async_session.execute.return_value = mock_result

        events = await outbox_repo.get_and_lock_pending_events(mock_async_session, limit=1)

        assert len(events) == 0
        mock_async_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_outbox_event(self, outbox_repo, mock_async_session):
        """Should create a new outbox event."""
        create_data = OutboxCreate(
            aggregate_type="memo",
            aggregate_id=str(uuid.uuid4()),
            event_type="MEMO_CREATED",
            payload={"memo_id": str(uuid.uuid4())},
        )
        # Mock the model that would be returned by session.add after flush
        created_outbox = Outbox(
            id=uuid.uuid4(),
            **create_data.model_dump(),
            status=EventStatus.PENDING,
            retry_count=0,
        )
        # Mock the refresh to return the created_outbox
        mock_async_session.refresh.side_effect = lambda obj: setattr(obj, "id", created_outbox.id)
        mock_async_session.add.return_value = None  # add doesn't return anything

        result = await outbox_repo.create(mock_async_session, create_data)

        mock_async_session.add.assert_called_once()
        mock_async_session.flush.assert_called_once()
        mock_async_session.refresh.assert_called_once()
        assert result.aggregate_type == create_data.aggregate_type

    @pytest.mark.asyncio
    async def test_update_outbox_event_status(self, outbox_repo, mock_async_session, sample_memo_id):
        """Should update an outbox event's status."""
        outbox_id = uuid.uuid4()
        update_data = OutboxUpdate(status=EventStatus.COMPLETED)

        # Mock the result of the update query
        mock_execute_result = AsyncMock()
        mock_execute_result.rowcount = 1
        mock_async_session.execute.return_value = mock_execute_result

        # Mock the result of the subsequent get query for return_updated_obj
        mock_outbox_event = Outbox(
            id=outbox_id,
            aggregate_type="memo",
            aggregate_id=str(sample_memo_id),
            event_type="MEMO_CREATED",
            payload={"memo_id": str(sample_memo_id)},
            status=EventStatus.COMPLETED,
            retry_count=0,
        )
        mock_get_result = MagicMock()
        mock_get_result.scalar_one_or_none.return_value = mock_outbox_event
        mock_async_session.execute.side_effect = [mock_execute_result, mock_get_result]

        result = await outbox_repo.update_by_pk(mock_async_session, outbox_id, update_data)

        assert result is not None
        assert result.status == EventStatus.COMPLETED
        mock_async_session.flush.assert_called_once()
        assert mock_async_session.execute.call_count == 2  # Called for UPDATE and then SELECT
