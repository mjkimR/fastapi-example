import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService


class TestNotificationServiceIntegration:
    """Integration app_tests for NotificationService."""

    @pytest.fixture
    def repo(self) -> NotificationRepository:
        return NotificationRepository()

    @pytest.fixture
    def service(self, repo: NotificationRepository) -> NotificationService:
        return NotificationService(repo=repo)

    @pytest.mark.asyncio
    async def test_create_notification(
        self,
        session: AsyncSession,
        service: NotificationService,
        regular_user,
        single_memo,
    ):
        notification_data = NotificationCreate(
            user_id=regular_user.id,
            message="Your memo was created by service!",
            resource_id=single_memo.id,
        )
        created_notification = await service.create(session, notification_data)
        await session.commit()

        assert created_notification is not None
        assert created_notification.id is not None
        assert created_notification.user_id == regular_user.id
        assert created_notification.message == notification_data.message

        retrieved_notification = await service.repo.get_by_pk(session, created_notification.id)
        assert retrieved_notification == created_notification
