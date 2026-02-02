import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.memos.enum import MemoEventType
from app.features.memos.models import Memo
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.features.memos.services import MemoContextKwargs, MemoService
from app.features.memos.usecases.crud import (
    CreateMemoUseCase,
    DeleteMemoUseCase,
    UpdateMemoUseCase,
)
from app.features.notifications.repos import NotificationRepository
from app.features.outbox.models import EventStatus
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.scheduler import process_outbox_events_job
from app.features.tags.repos import TagRepository
from app.features.tags.services import TagService
from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository


class TestOutboxToNotificationFlowIntegration:
    """
    Integration test for the entire outbox -> event dispatch -> notification flow.
    This app_tests the core asynchronous process by manually triggering the outbox job.
    """

    @pytest.fixture
    def outbox_repo(self) -> OutboxRepository:
        return OutboxRepository()

    @pytest.fixture
    def notification_repo(self) -> NotificationRepository:
        return NotificationRepository()

    @pytest.fixture
    def memo_repo(self) -> MemoRepository:
        return MemoRepository()

    @pytest.fixture
    def workspace_repo(self) -> WorkspaceRepository:
        return WorkspaceRepository()

    @pytest.fixture
    def tag_repo(self) -> TagRepository:
        return TagRepository()

    @pytest.fixture
    def memo_service(
        self,
        memo_repo: MemoRepository,
        workspace_repo: WorkspaceRepository,
        outbox_repo: OutboxRepository,
    ) -> MemoService:
        return MemoService(repo=memo_repo, parent_repo=workspace_repo, outbox_repo=outbox_repo)

    @pytest.fixture
    def tag_service(self, tag_repo: TagRepository, workspace_repo: WorkspaceRepository) -> TagService:
        return TagService(repo=tag_repo, parent_repo=workspace_repo)

    @pytest.fixture
    def create_memo_use_case(self, memo_service: MemoService, tag_service: TagService) -> CreateMemoUseCase:
        return CreateMemoUseCase(service=memo_service, tag_service=tag_service)

    @pytest.fixture
    def update_memo_use_case(self, memo_service: MemoService, tag_service: TagService) -> UpdateMemoUseCase:
        return UpdateMemoUseCase(service=memo_service, tag_service=tag_service)

    @pytest.fixture
    def delete_memo_use_case(self, memo_service: MemoService) -> DeleteMemoUseCase:
        return DeleteMemoUseCase(service=memo_service)

    async def _assert_outbox_and_notification_flow(
        self,
        session: AsyncSession,
        inspect_session: AsyncSession,
        outbox_repo: OutboxRepository,
        notification_repo: NotificationRepository,
        aggregate_id: str,
        user_id: str,
        expected_event_type: str,
        initial_notification_count: int,
    ):
        # 1. Assert: Check that an outbox event was created
        outbox_event = await outbox_repo.get(
            session,
            where=[
                OutboxRepository.model.aggregate_id == aggregate_id,
                OutboxRepository.model.event_type == expected_event_type,
            ],
        )
        assert outbox_event is not None
        assert outbox_event.status == EventStatus.PENDING

        # 2. Act: Manually run the outbox processing job
        await process_outbox_events_job()

        # 3. Assert: Check the final state
        # Re-fetch the outbox event and check its status is COMPLETED
        processed_outbox_event = await outbox_repo.get_by_pk(inspect_session, outbox_event.id)
        assert processed_outbox_event is not None
        assert processed_outbox_event.status == EventStatus.COMPLETED

        # Check that a new notification was created for the user
        notifications = await notification_repo.get_multi(
            inspect_session,
            where=[NotificationRepository.model.user_id == uuid.UUID(user_id)],
        )
        assert notifications.total_count == initial_notification_count + 1
        notification = notifications.items[0]
        assert str(notification.resource_id) == outbox_event.aggregate_id
        assert notification.event_type == expected_event_type

    @pytest.mark.asyncio
    async def test_memo_creation_triggers_notification_via_outbox(
        self,
        session: AsyncSession,
        inspect_session: AsyncSession,
        create_memo_use_case: CreateMemoUseCase,
        regular_user: User,
        single_workspace: Workspace,
        outbox_repo: OutboxRepository,
        notification_repo: NotificationRepository,
    ):
        """
        When a memo is created, an outbox event should be generated.
        Running the outbox processor should then create a notification.
        """
        memo_data = MemoCreate(
            category="Flow Test",
            title="Outbox Flow Memo",
            contents="This memo should trigger a notification.",
            tags=[],
        )
        context: MemoContextKwargs = {
            "parent_id": single_workspace.id,
            "user_id": regular_user.id,
        }
        initial_notifications = await notification_repo.get_multi(
            session, where=[NotificationRepository.model.user_id == regular_user.id]
        )

        created_memo = await create_memo_use_case.execute(memo_data, context=context)
        await session.commit()

        assert created_memo is not None

        assert initial_notifications.total_count is not None
        await self._assert_outbox_and_notification_flow(
            session,
            inspect_session,
            outbox_repo,
            notification_repo,
            str(created_memo.id),
            str(regular_user.id),
            MemoEventType.CREATE,
            initial_notifications.total_count,
        )

    @pytest.mark.asyncio
    async def test_memo_update_triggers_notification_via_outbox(
        self,
        session: AsyncSession,
        inspect_session: AsyncSession,
        update_memo_use_case: UpdateMemoUseCase,
        single_memo: Memo,
        regular_user: User,
        outbox_repo: OutboxRepository,
        notification_repo: NotificationRepository,
    ):
        """
        When a memo is updated, an outbox event should be generated.
        Running the outbox processor should then create a notification.
        """
        update_data = MemoUpdate(title="Updated Flow Title")
        context: MemoContextKwargs = {
            "parent_id": single_memo.workspace_id,
            "user_id": regular_user.id,
        }
        initial_notifications = await notification_repo.get_multi(
            session, where=[NotificationRepository.model.user_id == regular_user.id]
        )

        updated_memo = await update_memo_use_case.execute(single_memo.id, update_data, context)
        await session.commit()

        assert updated_memo is not None

        assert initial_notifications.total_count is not None
        await self._assert_outbox_and_notification_flow(
            session,
            inspect_session,
            outbox_repo,
            notification_repo,
            str(updated_memo.id),
            str(regular_user.id),
            MemoEventType.UPDATE,
            initial_notifications.total_count,
        )

    @pytest.mark.asyncio
    async def test_memo_deletion_triggers_notification_via_outbox(
        self,
        session: AsyncSession,
        inspect_session: AsyncSession,
        delete_memo_use_case: DeleteMemoUseCase,
        single_memo: Memo,
        regular_user: User,
        outbox_repo: OutboxRepository,
        notification_repo: NotificationRepository,
    ):
        """
        When a memo is deleted, an outbox event should be generated.
        Running the outbox processor should then create a notification.
        """
        memo_id = single_memo.id
        context: MemoContextKwargs = {
            "parent_id": single_memo.workspace_id,
            "user_id": regular_user.id,
        }
        initial_notifications = await notification_repo.get_multi(
            session, where=[NotificationRepository.model.user_id == regular_user.id]
        )

        result = await delete_memo_use_case.execute(memo_id, context)
        await session.commit()

        assert result.success is True

        assert initial_notifications.total_count is not None
        await self._assert_outbox_and_notification_flow(
            session,
            inspect_session,
            outbox_repo,
            notification_repo,
            str(memo_id),
            str(regular_user.id),
            MemoEventType.DELETE,
            initial_notifications.total_count,
        )
