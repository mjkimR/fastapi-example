import logging
from app.features.outbox.registry import register_event_handler
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.services import NotificationService
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.usecases.crud import CreateNotificationUseCase
from uuid import UUID

logger = logging.getLogger(__name__)


@register_event_handler("MEMO_CREATED")
async def handle_memo_created_event(payload: dict):
    """
    Handler called when the "MEMO_CREATED" event occurs.
    Creates a memo creation notification.
    """
    try:
        memo_id = UUID(payload["id"])
        created_by_user_id = UUID(payload["created_by"])

        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(service=notification_service)

        notification_data = NotificationCreate(
            user_id=created_by_user_id,
            message=f"A new memo '{payload.get('title', str(memo_id))}' has been created.",
            resource_id=memo_id,
            resource_type=notification_repo.model_name,
            event_type=payload.get("event_type", "MEMO_CREATED")
        )
        await create_notification_use_case.execute(notification_data)
        logger.info(f"Notification created for user {created_by_user_id} regarding memo {memo_id}.")
    except Exception as e:
        logger.error(f"Failed to create notification for memo {payload.get('memo_id')}: {e}")
