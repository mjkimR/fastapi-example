import logging
from app.features.memos.enum import MEMO_RES_NAME, MemoEventType
from app.features.memos.schemas import MemoNotificationPayload
from app.features.outbox.registry import register_event_handler
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.services import NotificationService
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.usecases.crud import CreateNotificationUseCase

logger = logging.getLogger(__name__)


@register_event_handler(MemoEventType.CREATE)
async def handle_memo_created_event(payload: dict):
    """
    Handler called when the "MEMO_CREATED" event occurs.
    Creates a memo creation notification.
    """
    try:
        payload_obj = MemoNotificationPayload.model_validate(payload)

        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(
            service=notification_service
        )

        notification_data = NotificationCreate(
            user_id=payload_obj.user_id,
            message=f"A new memo '{payload_obj.title}' has been created.",
            resource_id=payload_obj.id,
            resource_type=MEMO_RES_NAME,
            event_type=payload_obj.event_type.value,
        )
        await create_notification_use_case.execute(notification_data)
        logger.info(
            f"Notification created for user {payload_obj.user_id} regarding memo {payload_obj.id}."
        )
    except Exception as e:
        logger.error(
            f"Failed to create notification for memo {payload.get('memo_id')}: {e}"
        )
