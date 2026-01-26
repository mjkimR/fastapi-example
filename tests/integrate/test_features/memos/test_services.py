"""
Integration tests for MemoService.
Tests service layer operations with real database connections.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.memos.models import Memo
from app.features.memos.repos import MemoRepository
from app.features.memos.services import MemoService
from app.features.memos.schemas import MemoCreate, MemoUpdate


from app.features.workspaces.repos import WorkspaceRepository
from app.features.workspaces.models import Workspace
from app.features.auth.models import User


class TestMemoServiceIntegration:
    """Integration tests for MemoService with real database."""

    @pytest.fixture
    def repo(self) -> MemoRepository:
        """Create a MemoRepository instance."""
        return MemoRepository()

    @pytest.fixture
    def parent_repo(self) -> WorkspaceRepository:
        """Create a WorkspaceRepository instance."""
        return WorkspaceRepository()

    @pytest.fixture
    def service(self, repo: MemoRepository, parent_repo: WorkspaceRepository) -> MemoService:
        """Create a MemoService instance."""
        return MemoService(repo=repo, parent_repo=parent_repo)

    @pytest.mark.asyncio
    async def test_create_memo(self, session: AsyncSession, service: MemoService, single_workspace: Workspace, regular_user: User):
        """Should create a new memo through service."""
        memo_data = MemoCreate(
            category="Service Test",
            title="Service Integration Test",
            contents="Testing memo creation through service layer.",
            tags=[]
        )
        context = {"parent_id": single_workspace.id, "user_id": regular_user.id}

        result = await service.create(session, obj_data=memo_data, context=context)

        assert result is not None
        assert result.id is not None
        assert result.category == memo_data.category
        assert result.title == memo_data.title
        assert result.workspace_id == single_workspace.id
        assert result.created_by == regular_user.id

    @pytest.mark.asyncio
    async def test_get_memo(self, session: AsyncSession, service: MemoService, single_memo: Memo, regular_user: User):
        """Should retrieve a memo through service."""
        context = {"parent_id": single_memo.workspace_id, "user_id": regular_user.id}
        result = await service.get(session, obj_id=single_memo.id, context=context)

        assert result is not None
        assert result.id == single_memo.id

    @pytest.mark.asyncio
    async def test_get_multi_memos(self, session: AsyncSession, service: MemoService, sample_memos: list[Memo], single_workspace: Workspace, regular_user: User):
        """Should retrieve multiple memos through service."""
        context = {"parent_id": single_workspace.id, "user_id": regular_user.id}
        result = await service.get_multi(session, offset=0, limit=10, context=context)

        assert result.total_count >= len(sample_memos)
        assert len(result.items) >= 1

    @pytest.mark.asyncio
    async def test_update_memo(self, session: AsyncSession, service: MemoService, single_memo: Memo, admin_user: User):
        """Should update a memo through service."""
        update_data = MemoUpdate(title="Service Updated Title")
        context = {"parent_id": single_memo.workspace_id, "user_id": admin_user.id}

        result = await service.update(session, obj_id=single_memo.id, obj_data=update_data, context=context)

        assert result is not None
        assert result.title == "Service Updated Title"
        assert result.updated_by == admin_user.id

    @pytest.mark.asyncio
    async def test_delete_memo(self, session: AsyncSession, service: MemoService, single_memo: Memo, regular_user: User):
        """Should delete a memo through service."""
        context = {"parent_id": single_memo.workspace_id, "user_id": regular_user.id}
        result = await service.delete(session, obj_id=single_memo.id, context=context)

        assert result is True

        # Verify deletion
        deleted_memo = await service.get(session, obj_id=single_memo.id, context=context)
        assert deleted_memo is None
