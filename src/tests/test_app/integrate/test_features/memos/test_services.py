"""
Integration app_tests for MemoService.
Tests service layer operations with real database connections.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.memos.enum import MemoEventType
from app.features.memos.models import Memo
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoCreate, MemoUpdate
from app.features.memos.services import MemoContextKwargs, MemoService
from app.features.outbox.models import Outbox
from app.features.outbox.repos import OutboxRepository
from app.features.workspaces.models import Workspace
from app.features.workspaces.repos import WorkspaceRepository


class TestMemoServiceIntegration:
    """Integration app_tests for MemoService with real database."""

    @pytest.fixture
    def repo(self) -> MemoRepository:
        """Create a MemoRepository instance."""
        return MemoRepository()

    @pytest.fixture
    def parent_repo(self) -> WorkspaceRepository:
        """Create a WorkspaceRepository instance."""
        return WorkspaceRepository()

    @pytest.fixture
    def outbox_repo(self) -> OutboxRepository:
        """Create an OutboxRepository instance."""
        return OutboxRepository()

    @pytest.fixture
    def service(
        self,
        repo: MemoRepository,
        parent_repo: WorkspaceRepository,
        outbox_repo: OutboxRepository,
    ) -> MemoService:
        """Create a MemoService instance."""
        return MemoService(repo=repo, parent_repo=parent_repo, outbox_repo=outbox_repo)

    @pytest.mark.asyncio
    async def test_create_memo_and_creates_outbox_event(
        self,
        session: AsyncSession,
        service: MemoService,
        outbox_repo: OutboxRepository,
        single_workspace: Workspace,
        regular_user: User,
    ):
        """Should create a new memo and a corresponding outbox event."""
        memo_data = MemoCreate(
            category="Service Test",
            title="Service Integration Test",
            contents="Testing memo creation through service layer.",
            tags=[],
        )
        context: MemoContextKwargs = {
            "parent_id": single_workspace.id,
            "user_id": regular_user.id,
        }

        result = await service.create(session, obj_data=memo_data, context=context)
        await session.commit()  # Commit to make the outbox event visible

        assert result is not None
        assert result.id is not None
        assert result.title == memo_data.title

        # Verify outbox event
        outbox_event = await outbox_repo.get(session, where=[Outbox.aggregate_id == str(result.id)])
        assert outbox_event is not None
        assert outbox_event.event_type == MemoEventType.CREATE
        assert outbox_event.payload["title"] == result.title

    @pytest.mark.asyncio
    async def test_get_memo(
        self,
        session: AsyncSession,
        service: MemoService,
        single_memo: Memo,
        regular_user: User,
    ):
        """Should retrieve a memo through service."""
        context: MemoContextKwargs = {
            "parent_id": single_memo.workspace_id,
            "user_id": regular_user.id,
        }
        result = await service.get(session, obj_id=single_memo.id, context=context)

        assert result is not None
        assert result.id == single_memo.id

    @pytest.mark.asyncio
    async def test_get_multi_memos(
        self,
        session: AsyncSession,
        service: MemoService,
        sample_memos: list[Memo],
        single_workspace: Workspace,
        regular_user: User,
    ):
        """Should retrieve multiple memos through service."""
        context: MemoContextKwargs = {
            "parent_id": single_workspace.id,
            "user_id": regular_user.id,
        }
        result = await service.get_multi(session, offset=0, limit=10, context=context)

        assert result.total_count is not None
        assert result.total_count >= len(sample_memos)
        assert len(result.items) >= 1

    @pytest.mark.asyncio
    async def test_update_memo_and_creates_outbox_event(
        self,
        session: AsyncSession,
        service: MemoService,
        outbox_repo: OutboxRepository,
        single_memo: Memo,
        admin_user: User,
    ):
        """Should update a memo and create a corresponding outbox event."""
        update_data = MemoUpdate(title="Service Updated Title")
        context: MemoContextKwargs = {
            "parent_id": single_memo.workspace_id,
            "user_id": admin_user.id,
        }

        result = await service.update(session, obj_id=single_memo.id, obj_data=update_data, context=context)
        await session.commit()

        assert result is not None
        assert result.title == "Service Updated Title"
        assert result.updated_by == admin_user.id

        # Verify outbox event
        outbox_event = await outbox_repo.get(session, where=[Outbox.aggregate_id == str(result.id)])
        assert outbox_event is not None
        assert outbox_event.event_type == MemoEventType.UPDATE
        assert outbox_event.payload["title"] == "Service Updated Title"

    @pytest.mark.asyncio
    async def test_delete_memo_and_creates_outbox_event(
        self,
        session: AsyncSession,
        service: MemoService,
        outbox_repo: OutboxRepository,
        single_memo: Memo,
        regular_user: User,
    ):
        """Should delete a memo and create a corresponding outbox event."""
        memo_id = single_memo.id
        memo_title = single_memo.title
        context: MemoContextKwargs = {
            "parent_id": single_memo.workspace_id,
            "user_id": regular_user.id,
        }
        result = await service.delete(session, obj_id=memo_id, context=context)
        await session.commit()

        assert result.success is True

        # Verify deletion
        deleted_memo = await service.get(session, obj_id=memo_id, context=context)
        assert deleted_memo is None

        # Verify outbox event
        outbox_event = await outbox_repo.get(session, where=[Outbox.aggregate_id == str(memo_id)])
        assert outbox_event is not None
        assert outbox_event.event_type == MemoEventType.DELETE
        assert outbox_event.payload["title"] == memo_title
