from typing import Annotated

from fastapi import Depends

from app.base.services.base import BaseCreateServiceMixin
from app.features.notifications.models import Notification
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate


class NotificationService(
    BaseCreateServiceMixin[
        NotificationRepository, Notification, NotificationCreate, dict
    ],
):
    """Service class for handling notification operations."""

    context_model = dict  # No specific context needed for now

    def __init__(self, repo: Annotated[NotificationRepository, Depends()]):
        self._repo = repo

    @property
    def repo(self) -> NotificationRepository:
        return self._repo
