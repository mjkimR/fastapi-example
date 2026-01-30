from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends

from app.base.services.base import BaseContextKwargs
from app.core.database.transaction import AsyncTransaction
from app.features.notifications.models import Notification
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService


class CreateNotificationUseCase:
    def __init__(self, service: Annotated[NotificationService, Depends()]):
        self.service = service

    async def execute(
        self,
        notification_data: NotificationCreate,
        context: Optional[BaseContextKwargs] = None,
    ) -> Notification:
        async with AsyncTransaction() as session:
            notification = await self.service.create(
                session, notification_data, context=context
            )
            return notification
