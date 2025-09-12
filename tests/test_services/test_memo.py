import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memos import Memo
from app.repos.memos import MemoRepository
from app.schemas.memos import MemoCreate, MemoUpdate
from app.services.memos import MemoService


class TestMemoService:

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock(spec=MemoRepository)
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        return MemoService(repo=mock_repo)

    @pytest.mark.asyncio
    async def test_get_by_id(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        expected_result = MagicMock(spec=Memo)
        mock_repo.get_by_pk.return_value = expected_result

        # Act
        result = await service.get_by_id(session, test_id)

        # Assert
        mock_repo.get_by_pk.assert_awaited_once_with(session, pk=test_id)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_multi(self, service, mock_repo, session: AsyncSession):
        # Arrange
        expected_items = [MagicMock(spec=Memo) for _ in range(3)]
        mock_response = MagicMock()
        mock_response.items = expected_items
        mock_response.total = len(expected_items)
        mock_repo.get_multi.return_value = mock_response
        offset, limit = 0, 10

        # Act
        result = await service.get_multi(session, offset=offset, limit=limit)

        # Assert
        mock_repo.get_multi.assert_awaited_once_with(session, offset=offset, limit=limit)
        assert result.items == expected_items
        assert result.total == len(expected_items)

    @pytest.mark.asyncio
    async def test_create(self, service, mock_repo, session: AsyncSession):
        # Arrange
        create_data = MagicMock(spec=MemoCreate)
        expected_result = MagicMock(spec=Memo)
        mock_repo.create.return_value = expected_result

        # Act
        result = await service.create(session, create_data)

        # Assert
        mock_repo.create.assert_awaited_once_with(session, obj_in=create_data, commit=True)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_by_id(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        update_data = MagicMock(spec=MemoUpdate)
        expected_result = MagicMock(spec=Memo)
        mock_repo.update_by_pk.return_value = expected_result

        # Act
        result = await service.update_by_id(session, test_id, update_data)

        # Assert
        mock_repo.update_by_pk.assert_awaited_once_with(
            session, pk=test_id, obj_in=update_data, commit=True
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_delete_by_id(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        mock_repo.delete_by_pk.return_value = True

        # Act
        result = await service.delete_by_id(session, test_id)

        # Assert
        mock_repo.delete_by_pk.assert_awaited_once_with(
            session, pk=test_id, commit=True, soft_delete=False
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_by_id_failure(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        mock_repo.delete_by_pk.return_value = False

        # Act
        result = await service.delete_by_id(session, test_id)

        # Assert
        mock_repo.delete_by_pk.assert_awaited_once_with(
            session, pk=test_id, commit=True, soft_delete=False
        )
        assert result is False