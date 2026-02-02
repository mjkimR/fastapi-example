import uuid
from typing import cast
from unittest.mock import AsyncMock

import pytest

from app.features.notifications.models import Notification
from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService


class TestNotificationService:
    """Unit app_tests for NotificationService."""

    @pytest.fixture
    def mock_notification_repo(self) -> NotificationRepository:
        """Create a mock NotificationRepository instance."""
        return AsyncMock(spec=NotificationRepository)

    @pytest.fixture
    def notification_service(self, mock_notification_repo: NotificationRepository) -> NotificationService:
        """Create a NotificationService instance with a mocked repository."""
        return NotificationService(repo=mock_notification_repo)

    @pytest.mark.asyncio
    async def test_create_notification(
        self,
        notification_service: NotificationService,
        mock_notification_repo: NotificationRepository,
        mock_async_session,
        mock_user,
        mock_memo,
    ):
        """Should call repo.create with the correct NotificationCreate data."""
        create_data = NotificationCreate(
            user_id=mock_user.id,
            message="Test message",
            resource_id=mock_memo.id,
            resource_type="notification",
            event_type="TEST_EVENT",
        )
        repo_method = cast(AsyncMock, mock_notification_repo.create)
        repo_method.return_value = Notification(
            id=uuid.uuid4(),
            user_id=create_data.user_id,
            message=create_data.message,
            resource_id=create_data.resource_id,
            resource_type=create_data.resource_type,
            event_type=create_data.event_type,
        )

        result = await notification_service.create(mock_async_session, create_data)

        repo_method.assert_called_once_with(mock_async_session, obj_in=create_data)
        assert result.user_id == create_data.user_id
        assert result.message == create_data.message
        assert result.resource_id == create_data.resource_id
        assert result.resource_type == create_data.resource_type
        assert result.event_type == create_data.event_type
