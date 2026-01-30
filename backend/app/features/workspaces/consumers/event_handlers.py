import logging

from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService
from app.features.notifications.usecases.crud import CreateNotificationUseCase
from app.features.outbox.registry import register_event_handler
from app.features.workspaces.enum import WORKSPACE_RES_NAME
from app.features.workspaces.schemas import WorkspaceNotificationPayload

logger = logging.getLogger(__name__)


@register_event_handler("WORKSPACE_CREATED")
async def handle_workspace_created_event(payload: dict):
    """
    Handler called when the "WORKSPACE_CREATED" event occurs.
    Creates a workspace creation notification.
    """
    try:
        payload_obj = WorkspaceNotificationPayload.model_validate(payload)

        # Since this is a background task, manually create dependencies (AsyncTransaction is handled within UseCase)
        notification_repo = NotificationRepository()
        notification_service = NotificationService(repo=notification_repo)
        create_notification_use_case = CreateNotificationUseCase(
            service=notification_service
        )

        notification_data = NotificationCreate(
            user_id=payload_obj.user_id,
            message=f"A new workspace '{payload_obj.name}' has been created.",
            resource_id=payload_obj.id,
            resource_type=WORKSPACE_RES_NAME,
            event_type=payload_obj.event_type,
        )
        await create_notification_use_case.execute(notification_data)
        logger.info(
            f"Notification created for user {payload_obj.user_id} regarding workspace {payload_obj.id}."
        )
    except Exception as e:
        logger.error(
            f"Failed to create notification for workspace {payload.get('id')}: {e}"
        )
