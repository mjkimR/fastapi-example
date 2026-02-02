import logging

from app.features.memos.enum import MemoEventType
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoNotificationPayload
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService
from app.features.notifications.usecases.crud import CreateNotificationUseCase
from app.features.outbox.registry import register_event_handler
from app_base.base.exceptions.event import (
    EventProcessingException,
    InvalidEventPayloadException,
)
from app_base.base.schemas.event import DomainEvent

logger = logging.getLogger(__name__)


@register_event_handler(MemoEventType.CREATE)
async def handle_memo_created_event(event: DomainEvent):
    """
    Handler called when the "MEMO_CREATED" event occurs.
    Creates a memo creation notification.
    """
    try:
        payload = event.parse_payload(MemoNotificationPayload)
    except Exception as e:
        raise InvalidEventPayloadException("Invalid payload for memo created event") from e

    try:
        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=payload.user_id,
            message=f"A new memo '{payload.title}' has been created.",
            resource_id=payload.id,
            resource_type=MemoRepository.model_name(),
            event_type=payload.event_type.value,
        )
        await create_notification_use_case.execute(notification_data)
        logger.debug(f"Notification created for user {payload.user_id} regarding memo {payload.id}.")
    except Exception as e:
        raise EventProcessingException(f"Failed to create notification for memo {payload.id}") from e


@register_event_handler(MemoEventType.UPDATE)
async def handle_memo_updated_event(event: DomainEvent):
    """
    Handler called when the "MEMO_UPDATED" event occurs.
    Creates a memo update notification.
    """
    try:
        payload = event.parse_payload(MemoNotificationPayload)
    except Exception as e:
        raise InvalidEventPayloadException("Invalid payload for memo updated event") from e

    try:
        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=payload.user_id,
            message=f"The memo '{payload.title}' has been updated.",
            resource_id=payload.id,
            resource_type=MemoRepository.model_name(),
            event_type=payload.event_type.value,
        )
        await create_notification_use_case.execute(notification_data)
        logger.debug(f"Notification created for user {payload.user_id} regarding memo {payload.id}.")
    except Exception as e:
        raise EventProcessingException(f"Failed to create notification for memo {payload.id}") from e


@register_event_handler(MemoEventType.DELETE)
async def handle_memo_deleted_event(event: DomainEvent):
    """
    Handler called when the "MEMO_DELETED" event occurs.
    Creates a memo deletion notification.
    """
    try:
        payload = event.parse_payload(MemoNotificationPayload)
    except Exception as e:
        raise InvalidEventPayloadException("Invalid payload for memo deleted event") from e

    try:
        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=payload.user_id,
            message=f"The memo '{payload.title}' has been deleted.",
            resource_id=payload.id,
            resource_type=MemoRepository.model_name(),
            event_type=payload.event_type.value,
        )
        await create_notification_use_case.execute(notification_data)
        logger.debug(f"Notification created for user {payload.user_id} regarding memo {payload.id}.")
    except Exception as e:
        raise EventProcessingException(f"Failed to create notification for memo {payload.id}") from e
