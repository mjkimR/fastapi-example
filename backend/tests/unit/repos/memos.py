import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.features import Memo
from backend.app.features.memos.repos import MemoRepository


class TestMemoRepositoryUnit:
    @pytest.fixture
    def mock_session(self):
        """Mock AsyncSession"""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def memo_repo(self):
        return MemoRepository()

    @pytest.fixture
    def sample_memo(self):
        return Memo(
            id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
            category="test",
            title="Test Memo",
            contents="Test Contents"
        )

    async def test_get_by_pk_calls_correct_query(self, memo_repo, mock_session, sample_memo):
        """Verify that the correct query is generated when querying by PK"""
        # Mock setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_memo
        mock_session.execute.return_value = mock_result

        # Execute
        result = await memo_repo.get_by_pk(mock_session, uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))

        # Verify
        assert result == sample_memo
        mock_session.execute.assert_called_once()

        # Check executed query
        called_stmt = mock_session.execute.call_args[0][0]
        assert "SELECT" in str(called_stmt)
        assert "memos" in str(called_stmt)

    async def test_get_by_pk_returns_none_when_not_found(self, memo_repo, mock_session):
        """Verify that None is returned when querying for a non-existent PK"""
        # Mock setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await memo_repo.get_by_pk(mock_session, uuid.UUID("550e8400-e29b-41d4-a716-446655440000"))

        # Verify
        assert result is None
        mock_session.execute.assert_called_once()

    def test_primary_key_filters_invalid_count(self, memo_repo):
        """Test exception when providing incorrect number of primary key values"""
        with pytest.raises(ValueError, match="Incorrect number of primary key values"):
            memo_repo._get_primary_key_filters([uuid.uuid4(), uuid.uuid4()])  # Memo has single PK

    async def test_get_with_empty_where_condition(self, memo_repo):
        """Test query generation with empty WHERE condition"""
        stmt = memo_repo._select(where=[])

        # Verify that query is generated correctly even with empty condition
        query_str = str(stmt)
        assert "SELECT" in query_str
        assert "FROM memos" in query_str
