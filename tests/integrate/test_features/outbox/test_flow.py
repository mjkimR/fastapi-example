import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.workspaces.models import Workspace
from app.features.memos.schemas import MemoCreate
from app.features.memos.usecases.crud import CreateMemoUseCase
from app.features.memos.repos import MemoRepository
from app.features.memos.services import MemoContextKwargs, MemoService
from app.features.tags.repos import TagRepository
from app.features.tags.services import TagService
from app.features.outbox.services import OutboxService
from app.features.outbox.repos import OutboxRepository
from app.features.outbox.models import EventStatus
from app.features.outbox.scheduler import process_outbox_events_job
from app.features.notifications.repos import NotificationRepository
from app.features.workspaces.repos import WorkspaceRepository


class TestOutboxToNotificationFlowIntegration:
    """
    Integration test for the entire outbox -> event dispatch -> notification flow.
    This tests the core asynchronous process by manually triggering the outbox job.
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
        self, memo_repo: MemoRepository, workspace_repo: WorkspaceRepository
    ) -> MemoService:
        return MemoService(repo=memo_repo, parent_repo=workspace_repo)

    @pytest.fixture
    def tag_service(
        self, tag_repo: TagRepository, workspace_repo: WorkspaceRepository
    ) -> TagService:
        return TagService(repo=tag_repo, parent_repo=workspace_repo)

    @pytest.fixture
    def outbox_service_for_uc(self, outbox_repo: OutboxRepository) -> OutboxService:
        # Use a different name to avoid conflict with `outbox_service` in the main app
        return OutboxService(repo=outbox_repo)

    @pytest.fixture
    def create_memo_use_case(
        self,
        memo_service: MemoService,
        tag_service: TagService,
        outbox_service_for_uc: OutboxService,
    ) -> CreateMemoUseCase:
        return CreateMemoUseCase(
            memo_service=memo_service,
            tag_service=tag_service,
            outbox_service=outbox_service_for_uc,
        )

    @pytest.mark.asyncio
    async def test_memo_creation_triggers_notification_via_outbox(
        self,
        session: AsyncSession,
        inspect_session: AsyncSession,
        create_memo_use_case: CreateMemoUseCase,  # Already has outbox_service injected
        regular_user: User,
        single_workspace: Workspace,
        outbox_repo: OutboxRepository,
        notification_repo: NotificationRepository,
    ):
        """
        When a memo is created, an outbox event should be generated.
        Running the outbox processor should then create a notification.
        """
        # 1. Arrange: Create a memo using the use case (this should create an outbox event)
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

        created_memo = await create_memo_use_case.execute(memo_data, context=context)

        # Ensure transaction is committed so outbox event is visible to scheduler
        await session.commit()

        assert created_memo is not None
        assert created_memo.id is not None

        # 2. Assert: Check that an outbox event was created for MEMO_CREATED
        outbox_events_before_processing = await outbox_repo.get_multi(
            session, where=[OutboxRepository.model.event_type == "MEMO_CREATED"]
        )
        assert outbox_events_before_processing.total_count == 1
        outbox_event = outbox_events_before_processing.items[0]
        assert outbox_event.aggregate_id == str(created_memo.id)
        assert outbox_event.status == EventStatus.PENDING

        # 3. Act: Manually run the outbox processing job
        await process_outbox_events_job()  # Call the job directly

        # 4. Assert: Check the final state
        # Re-fetch the outbox event and check its status
        processed_outbox_event = await outbox_repo.get_by_pk(
            inspect_session, outbox_event.id
        )
        assert processed_outbox_event is not None
        assert processed_outbox_event.status == EventStatus.COMPLETED

        # Check that a notification was created for the user
        notifications = await notification_repo.get_multi(
            inspect_session,
            where=[NotificationRepository.model.user_id == regular_user.id],
        )
        assert notifications.total_count == 1
        notification = notifications.items[0]
        assert notification.resource_id == created_memo.id
