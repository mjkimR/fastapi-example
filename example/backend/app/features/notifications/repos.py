from app_kit.base.repos.base import BaseRepository
from app.features.notifications.models import Notification
from app.features.notifications.schemas import (
    NotificationCreate,
    NotificationUpdate,
)


class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationUpdate]):
    model = Notification
