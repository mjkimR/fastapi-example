"""
Integration app_tests for MemoRepository.
Tests CRUD operations with real database connections.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.memos.models import Memo
from app.features.memos.repos import MemoRepository
from app.features.memos.schemas import MemoCreate, MemoUpdate


class TestMemoRepositoryIntegration:
    """Integration app_tests for MemoRepository with real database."""

    @pytest.fixture
    def repo(self) -> MemoRepository:
        """Create a MemoRepository instance."""
        return MemoRepository()

    @pytest.mark.asyncio
    async def test_create_memo(
        self,
        session: AsyncSession,
        repo: MemoRepository,
        single_workspace,
        regular_user,
    ):
        """Should create a new memo in the database."""
        memo_data = MemoCreate(
            category="Test",
            title="Integration Test Memo",
            contents="This is an integration test memo.",
            tags=[],
        )

        result = await repo.create(
            session,
            obj_in=memo_data,
            workspace_id=single_workspace.id,
            created_by=regular_user.id,
            updated_by=regular_user.id,
        )

        assert result is not None
        assert result.id is not None
        assert result.category == memo_data.category
        assert result.title == memo_data.title
        assert result.contents == memo_data.contents
        assert result.workspace_id == single_workspace.id
        assert result.created_by == regular_user.id

    @pytest.mark.asyncio
    async def test_get_memo_by_pk(self, session: AsyncSession, repo: MemoRepository, single_memo: Memo):
        """Should retrieve a memo by primary key."""
        result = await repo.get_by_pk(session, pk=single_memo.id)

        assert result is not None
        assert result.id == single_memo.id
        assert result.title == single_memo.title

    @pytest.mark.asyncio
    async def test_get_memo_by_pk_not_found(self, session: AsyncSession, repo: MemoRepository):
        """Should return None when memo not found."""
        non_existent_id = uuid.uuid4()

        result = await repo.get_by_pk(session, pk=non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_memos(self, session: AsyncSession, repo: MemoRepository, sample_memos: list[Memo]):
        """Should retrieve multiple memos with pagination."""
        result = await repo.get_multi(session, offset=0, limit=10)

        assert result.total_count is not None
        assert result.total_count >= len(sample_memos)
        assert len(result.items) <= 10

    @pytest.mark.asyncio
    async def test_get_multi_memos_with_offset(
        self, session: AsyncSession, repo: MemoRepository, sample_memos: list[Memo]
    ):
        """Should retrieve memos with offset."""
        result = await repo.get_multi(session, offset=1, limit=10)

        assert result.total_count is not None
        assert result.offset == 1
        assert len(result.items) <= result.total_count - 1

    @pytest.mark.asyncio
    async def test_get_memo_with_where_clause(
        self, session: AsyncSession, repo: MemoRepository, sample_memos: list[Memo]
    ):
        """Should filter memos with where clause."""
        target_category = sample_memos[0].category

        result = await repo.get(session, where=Memo.category == target_category)

        assert result is not None
        assert result.category == target_category

    @pytest.mark.asyncio
    async def test_update_memo_by_pk(self, session: AsyncSession, repo: MemoRepository, single_memo: Memo, admin_user):
        """Should update an existing memo."""
        update_data = MemoUpdate(title="Updated Title", contents="Updated contents")

        result = await repo.update_by_pk(session, pk=single_memo.id, obj_in=update_data, updated_by=admin_user.id)

        assert result is not None
        assert result.title == "Updated Title"
        assert result.contents == "Updated contents"
        assert result.updated_by == admin_user.id

    @pytest.mark.asyncio
    async def test_update_memo_partial(
        self, session: AsyncSession, repo: MemoRepository, single_memo: Memo, admin_user
    ):
        """Should partially update a memo."""
        original_contents = single_memo.contents
        update_data = MemoUpdate(title="Partial Update Title")

        result = await repo.update_by_pk(session, pk=single_memo.id, obj_in=update_data, updated_by=admin_user.id)

        assert result is not None
        assert result.title == "Partial Update Title"
        assert result.contents == original_contents
        assert result.updated_by == admin_user.id

    @pytest.mark.asyncio
    async def test_update_nonexistent_memo(self, session: AsyncSession, repo: MemoRepository):
        """Should return None when updating non-existent memo."""
        non_existent_id = uuid.uuid4()
        update_data = MemoUpdate(title="Updated Title")

        result = await repo.update_by_pk(session, pk=non_existent_id, obj_in=update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_memo_by_pk(self, session: AsyncSession, repo: MemoRepository, single_memo: Memo):
        """Should delete a memo from the database."""
        memo_id = single_memo.id

        result = await repo.delete_by_pk(session, pk=memo_id)

        assert result is True

        # Verify deletion
        deleted_memo = await repo.get_by_pk(session, pk=memo_id)
        assert deleted_memo is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_memo(self, session: AsyncSession, repo: MemoRepository):
        """Should return False when deleting non-existent memo."""
        non_existent_id = uuid.uuid4()

        result = await repo.delete_by_pk(session, pk=non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_memo(self, session: AsyncSession, repo: MemoRepository, single_memo: Memo):
        """Should check if memo exists."""
        result = await repo.exists(session, where=Memo.id == single_memo.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_memo_not_found(self, session: AsyncSession, repo: MemoRepository):
        """Should return False when memo does not exist."""
        non_existent_id = uuid.uuid4()

        result = await repo.exists(session, where=Memo.id == non_existent_id)

        assert result is False
