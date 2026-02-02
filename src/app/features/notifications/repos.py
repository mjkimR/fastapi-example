from app.features.notifications.models import Notification
from app.features.notifications.schemas import (
    NotificationCreate,
    NotificationUpdate,
)
from app_base.base.repos.base import BaseRepository


class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationUpdate]):
    model = Notification
