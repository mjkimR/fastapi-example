import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate


class TestNotificationRepositoryIntegration:
    """Integration app_tests for NotificationRepository with real database."""

    @pytest.fixture
    def repo(self) -> NotificationRepository:
        """Create a NotificationRepository instance."""
        return NotificationRepository()

    @pytest.mark.asyncio
    async def test_create_notification(
        self,
        session: AsyncSession,
        repo: NotificationRepository,
        regular_user,
        single_memo,
    ):
        """Should create a new notification in the database."""
        notification_data = NotificationCreate(
            user_id=regular_user.id,
            message="Your memo was created!",
            resource_id=single_memo.id,
            resource_type=repo.model_name(),
            event_type="MEMO_CREATED",
        )

        result = await repo.create(session, notification_data)
        await session.commit()

        assert result is not None
        assert result.id is not None
        assert result.user_id == notification_data.user_id
        assert result.message == notification_data.message
        assert result.resource_id == notification_data.resource_id
        assert result.resource_type == notification_data.resource_type
        assert result.event_type == notification_data.event_type
        assert result.is_read is False

        retrieved = await repo.get_by_pk(session, result.id)
        assert retrieved == result
