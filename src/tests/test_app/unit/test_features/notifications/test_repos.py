import uuid

import pytest

from app.features.notifications.models import Notification
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate


class TestNotificationRepository:
    """Unit app_tests for NotificationRepository."""

    @pytest.fixture
    def notification_repo(self):
        """Create NotificationRepository instance."""
        return NotificationRepository()

    @pytest.mark.asyncio
    async def test_model_is_notification(self, notification_repo):
        """Should have Notification as model."""
        assert notification_repo.model == Notification

    @pytest.mark.asyncio
    async def test_create_notification(self, notification_repo, mock_async_session, mock_user, mock_memo):
        """Should create a new notification."""
        create_data = NotificationCreate(
            user_id=mock_user.id,
            message="New memo created!",
            resource_id=mock_memo.id,
            resource_type=notification_repo.model_name(),
            event_type="MEMO_CREATED",
        )

        # Mock the refresh to return the created_notification
        created_notification = Notification(
            id=uuid.uuid4(),
            user_id=create_data.user_id,
            message=create_data.message,
            resource_id=create_data.resource_id,
        )
        mock_async_session.refresh.side_effect = lambda obj: setattr(obj, "id", created_notification.id)
        mock_async_session.add.return_value = None

        result = await notification_repo.create(mock_async_session, create_data)

        mock_async_session.add.assert_called_once()
        mock_async_session.flush.assert_called_once()
        mock_async_session.refresh.assert_called_once()
        assert result.user_id == create_data.user_id
        assert result.message == create_data.message
        assert result.resource_id == create_data.resource_id
        assert result.resource_type == create_data.resource_type
        assert result.event_type == create_data.event_type
