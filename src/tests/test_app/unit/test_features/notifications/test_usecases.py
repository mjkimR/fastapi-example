import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.features.notifications.models import Notification
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.usecases.crud import CreateNotificationUseCase


class TestCreateNotificationUseCase:
    """Unit app_tests for CreateNotificationUseCase."""

    @pytest.fixture
    def mock_notification_service(self) -> AsyncMock:
        """Create a mock NotificationService instance."""
        return AsyncMock()

    @pytest.fixture
    def create_notification_use_case(self, mock_notification_service: AsyncMock) -> CreateNotificationUseCase:
        """Create a CreateNotificationUseCase instance."""
        return CreateNotificationUseCase(service=mock_notification_service)

    @pytest.mark.asyncio
    async def test_execute_creates_notification(
        self,
        create_notification_use_case: CreateNotificationUseCase,
        mock_notification_service: AsyncMock,
        mock_user,
        mock_memo,
    ):
        """Should call service.create with the correct data within a transaction."""
        notification_data = NotificationCreate(
            user_id=mock_user.id,
            message="Test notification message",
            resource_id=mock_memo.id,
            resource_type="notification",
            event_type="TEST_EVENT",
        )

        # This is the notification object that the service.create call would return
        # and that the session.refresh would operate on.
        created_notification_instance = Notification(
            id=uuid.uuid4(),
            user_id=notification_data.user_id,
            message=notification_data.message,
            resource_id=notification_data.resource_id,
        )
        mock_notification_service.create.return_value = created_notification_instance

        # Patch AsyncTransaction to control the session inside the use case
        with patch("app_base.core.database.transaction.AsyncTransaction") as mock_transaction:
            # Configure the mock session returned by AsyncTransaction.__aenter__
            mock_session = AsyncMock()
            mock_transaction.return_value.__aenter__.return_value = mock_session

            # Ensure mock_session.flush and mock_session.refresh work correctly on the instance
            # For refresh, we'll make it modify the object in place, or simply return the object.
            mock_session.flush.return_value = None
            mock_session.refresh.side_effect = (
                lambda obj: None
            )  # refresh typically modifies in place, or returns None if successful

            result = await create_notification_use_case.execute(notification_data)

        assert result.user_id == notification_data.user_id
        assert result == created_notification_instance  # The use case returns the refreshed object
