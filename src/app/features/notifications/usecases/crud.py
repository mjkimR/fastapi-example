from typing import Annotated, Optional

from fastapi import Depends

from app.features.notifications.models import Notification
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService
from app_base.base.services.base import BaseContextKwargs
from app_base.core.database.transaction import AsyncTransaction


class CreateNotificationUseCase:
    def __init__(self, service: Annotated[NotificationService, Depends()]):
        self.service = service

    async def execute(
        self,
        notification_data: NotificationCreate,
        context: Optional[BaseContextKwargs] = None,
    ) -> Notification:
        async with AsyncTransaction() as session:
            notification = await self.service.create(session, notification_data, context=context)
            return notification
