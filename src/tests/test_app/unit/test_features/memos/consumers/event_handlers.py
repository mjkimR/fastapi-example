from unittest.mock import patch

import pytest

from app.features.memos.consumers.event_handlers import (
    handle_memo_created_event,
    handle_memo_deleted_event,
    handle_memo_updated_event,
)
from app.features.memos.enum import MemoEventType
from app.features.memos.schemas import MemoNotificationPayload
from app_base.base.exceptions.event import (
    EventProcessingException,
    InvalidEventPayloadException,
)
from app_base.base.schemas.event import DomainEvent


@pytest.fixture
def mock_create_notification_use_case():
    with patch("app.features.memos.consumers.event_handlers.CreateNotificationUseCase") as mock_use_case:
        yield mock_use_case


class TestMemoEventHandlers:
    """Unit app_tests for memo event handlers."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "handler, event_type",
        [
            (handle_memo_created_event, MemoEventType.CREATE),
            (handle_memo_updated_event, MemoEventType.UPDATE),
            (handle_memo_deleted_event, MemoEventType.DELETE),
        ],
    )
    async def test_handler_creates_notification(
        self,
        handler,
        event_type,
        mock_create_notification_use_case,
        mock_user,
        mock_memo,
    ):
        """Should correctly parse payload and trigger notification creation."""
        payload = MemoNotificationPayload(
            id=mock_memo.id,
            workspace_id=mock_memo.workspace_id,
            user_id=mock_user.id,
            title=mock_memo.title,
            event_type=event_type,
        )
        event = DomainEvent(event_type=event_type, payload=payload.model_dump(mode="json"))

        await handler(event)

        # Check that a notification use case was instantiated and executed
        execute_spy = mock_create_notification_use_case.return_value.execute
        execute_spy.assert_called_once()
        call_args = execute_spy.call_args[0][0]

        assert call_args.user_id == payload.user_id
        assert call_args.resource_id == payload.id
        assert call_args.event_type == event_type.value

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "handler, event_type",
        [
            (handle_memo_created_event, MemoEventType.CREATE),
            (handle_memo_updated_event, MemoEventType.UPDATE),
            (handle_memo_deleted_event, MemoEventType.DELETE),
        ],
    )
    async def test_handler_raises_invalid_payload_exception(self, handler, event_type):
        """Should raise InvalidEventPayloadException for a bad payload."""
        event = DomainEvent(event_type=event_type, payload={"invalid": "payload"})

        with pytest.raises(InvalidEventPayloadException):
            await handler(event)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "handler, event_type",
        [
            (handle_memo_created_event, MemoEventType.CREATE),
            (handle_memo_updated_event, MemoEventType.UPDATE),
            (handle_memo_deleted_event, MemoEventType.DELETE),
        ],
    )
    async def test_handler_raises_event_processing_exception_on_failure(
        self,
        handler,
        event_type,
        mock_create_notification_use_case,
        mock_memo,
        mock_user,
    ):
        """Should raise EventProcessingException if notification creation fails."""
        payload = MemoNotificationPayload(
            id=mock_memo.id,
            workspace_id=mock_memo.workspace_id,
            user_id=mock_user.id,
            title=mock_memo.title,
            event_type=event_type,
        )
        event = DomainEvent(event_type=event_type, payload=payload.model_dump(mode="json"))
        mock_create_notification_use_case.return_value.execute.side_effect = Exception("DB error")

        with pytest.raises(EventProcessingException):
            await handler(event)
