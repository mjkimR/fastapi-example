from app.base.repos.base import BaseRepository
from app.features.notifications.models import Notification
from app.features.notifications.schemas import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)


class NotificationRepository(
    BaseRepository[Notification, NotificationCreate, NotificationUpdate]
):
    model = Notification
