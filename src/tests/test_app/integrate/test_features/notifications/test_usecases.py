import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.notifications.repos import NotificationRepository
from app.features.notifications.schemas import NotificationCreate
from app.features.notifications.services import NotificationService
from app.features.notifications.usecases.crud import CreateNotificationUseCase


class TestCreateNotificationUseCaseIntegration:
    """Integration app_tests for CreateNotificationUseCase."""

    @pytest.fixture
    def repo(self) -> NotificationRepository:
        return NotificationRepository()

    @pytest.fixture
    def service(self, repo: NotificationRepository) -> NotificationService:
        return NotificationService(repo=repo)

    @pytest.fixture
    def use_case(self, service: NotificationService) -> CreateNotificationUseCase:
        return CreateNotificationUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_creates_notification(
        self,
        session: AsyncSession,
        use_case: CreateNotificationUseCase,
        regular_user,
        single_memo,
    ):
        notification_data = NotificationCreate(
            user_id=regular_user.id,
            message="Your memo was created by use case!",
            resource_id=single_memo.id,
        )
        created_notification = await use_case.execute(notification_data)
        # No need to commit here, use_case.execute handles its own transaction

        assert created_notification is not None
        assert created_notification.id is not None
        assert created_notification.user_id == regular_user.id
        assert created_notification.message == notification_data.message

        # Verify it's in the DB by retrieving it through service
        retrieved_notification = await use_case.service.repo.get_by_pk(session, created_notification.id)
        assert retrieved_notification is not None
        assert retrieved_notification.id == created_notification.id
