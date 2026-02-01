import logging

from app_kit.base.exceptions.event import (
    EventProcessingException,
    InvalidEventPayloadException,
)
from app_kit.base.schemas.event import DomainEvent
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService
from app.features.notifications.usecases.crud import CreateNotificationUseCase
from app.features.outbox.registry import register_event_handler
from app.features.workspaces.enum import WorkspaceEventType
from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.schemas import WorkspaceNotificationPayload

logger = logging.getLogger(__name__)


@register_event_handler(WorkspaceEventType.CREATE)
async def handle_workspace_created_event(event: DomainEvent):
    """
    Handler called when the "WORKSPACE_CREATED" event occurs.
    Creates a workspace creation notification.
    """
    try:
        payload = event.parse_payload(WorkspaceNotificationPayload)
    except Exception as e:
        raise InvalidEventPayloadException("Invalid payload for workspace created event") from e

    try:
        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=payload.user_id,
            message=f"A new workspace '{payload.name}' has been created.",
            resource_id=payload.id,
            resource_type=WorkspaceRepository.model_name(),
            event_type=payload.event_type,
        )
        await create_notification_use_case.execute(notification_data)
        logger.debug(f"Notification created for user {payload.user_id} regarding workspace {payload.id}.")
    except Exception as e:
        raise EventProcessingException(f"Failed to create notification for workspace {payload.id}") from e


@register_event_handler(WorkspaceEventType.UPDATE)
async def handle_workspace_updated_event(event: DomainEvent):
    """
    Handler called when the "WORKSPACE_UPDATED" event occurs.
    Creates a workspace update notification.
    """
    try:
        payload = event.parse_payload(WorkspaceNotificationPayload)
    except Exception as e:
        raise InvalidEventPayloadException("Invalid payload for workspace updated event") from e

    try:
        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=payload.user_id,
            message=f"The workspace '{payload.name}' has been updated.",
            resource_id=payload.id,
            resource_type=WorkspaceRepository.model_name(),
            event_type=payload.event_type,
        )
        await create_notification_use_case.execute(notification_data)
        logger.debug(f"Notification created for user {payload.user_id} regarding workspace {payload.id}.")
    except Exception as e:
        raise EventProcessingException(f"Failed to create notification for workspace {payload.id}") from e


@register_event_handler(WorkspaceEventType.DELETE)
async def handle_workspace_deleted_event(event: DomainEvent):
    """
    Handler called when the "WORKSPACE_DELETED" event occurs.
    Creates a workspace deletion notification.
    """
    try:
        payload = event.parse_payload(WorkspaceNotificationPayload)
    except Exception as e:
        raise InvalidEventPayloadException("Invalid payload for workspace deleted event") from e

    try:
        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=payload.user_id,
            message=f"The workspace '{payload.name}' has been deleted.",
            resource_id=payload.id,
            resource_type=WorkspaceRepository.model_name(),
            event_type=payload.event_type,
        )
        await create_notification_use_case.execute(notification_data)
        logger.debug(f"Notification created for user {payload.user_id} regarding workspace {payload.id}.")
    except Exception as e:
        raise EventProcessingException(f"Failed to create notification for workspace {payload.id}") from e
