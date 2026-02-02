from unittest.mock import patch

import pytest

from app.features.workspaces.consumers.event_handlers import (
    handle_workspace_created_event,
    handle_workspace_deleted_event,
    handle_workspace_updated_event,
)
from app.features.workspaces.enum import WorkspaceEventType
from app.features.workspaces.schemas import WorkspaceNotificationPayload
from app_base.base.exceptions.event import (
    EventProcessingException,
    InvalidEventPayloadException,
)
from app_base.base.schemas.event import DomainEvent


@pytest.fixture
def mock_create_notification_use_case():
    with patch("app.features.workspaces.consumers.event_handlers.CreateNotificationUseCase") as mock_use_case:
        yield mock_use_case


class TestWorkspaceEventHandlers:
    """Unit app_tests for workspace event handlers."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "handler, event_type",
        [
            (handle_workspace_created_event, WorkspaceEventType.CREATE),
            (handle_workspace_updated_event, WorkspaceEventType.UPDATE),
            (handle_workspace_deleted_event, WorkspaceEventType.DELETE),
        ],
    )
    async def test_handler_creates_notification(
        self,
        handler,
        event_type,
        mock_create_notification_use_case,
        mock_user,
        mock_workspace,
    ):
        """Should correctly parse payload and trigger notification creation."""
        payload = WorkspaceNotificationPayload(
            id=mock_workspace.id,
            name=mock_workspace.name,
            user_id=mock_user.id,
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
            (handle_workspace_created_event, WorkspaceEventType.CREATE),
            (handle_workspace_updated_event, WorkspaceEventType.UPDATE),
            (handle_workspace_deleted_event, WorkspaceEventType.DELETE),
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
            (handle_workspace_created_event, WorkspaceEventType.CREATE),
            (handle_workspace_updated_event, WorkspaceEventType.UPDATE),
            (handle_workspace_deleted_event, WorkspaceEventType.DELETE),
        ],
    )
    async def test_handler_raises_event_processing_exception_on_failure(
        self,
        handler,
        event_type,
        mock_create_notification_use_case,
        mock_workspace,
        mock_user,
    ):
        """Should raise EventProcessingException if notification creation fails."""
        payload = WorkspaceNotificationPayload(
            id=mock_workspace.id,
            name=mock_workspace.name,
            user_id=mock_user.id,
            event_type=event_type,
        )
        event = DomainEvent(event_type=event_type, payload=payload.model_dump(mode="json"))
        mock_create_notification_use_case.return_value.execute.side_effect = Exception("DB error")

        with pytest.raises(EventProcessingException):
            await handler(event)
