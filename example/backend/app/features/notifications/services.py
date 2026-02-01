from typing import Annotated

from fastapi import Depends

from app_kit.base.services.base import BaseContextKwargs, BaseCreateServiceMixin
from app.features.notifications.models import Notification
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate


class NotificationService(
    BaseCreateServiceMixin[NotificationRepository, Notification, NotificationCreate, BaseContextKwargs],
):
    """Service class for handling notification operations."""

    def __init__(self, repo: Annotated[NotificationRepository, Depends()]):
        self._repo = repo

    @property
    def repo(self) -> NotificationRepository:
        return self._repo

    @property
    def context_model(self):
        return BaseContextKwargs
