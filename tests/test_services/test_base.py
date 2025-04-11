import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base import BaseService
from app.repos.base import BaseRepository, GetMultiResponseModel


class TestBaseService:

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock(spec=BaseRepository)
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        return BaseService(repo=mock_repo)

    @pytest.mark.asyncio
    async def test_get_by_id(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        expected_result = MagicMock()
        mock_repo.get_by_pk.return_value = expected_result

        # Act
        result = await service.get_by_id(session, test_id)

        # Assert
        mock_repo.get_by_pk.assert_awaited_once_with(session, pk=test_id)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_multi(self, service, mock_repo, session: AsyncSession):
        # Arrange
        expected_result = MagicMock(spec=GetMultiResponseModel)
        mock_repo.get_multi.return_value = expected_result
        offset, limit = 10, 20

        # Act
        result = await service.get_multi(session, offset=offset, limit=limit)

        # Assert
        mock_repo.get_multi.assert_awaited_once_with(session, offset=offset, limit=limit)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_create(self, service, mock_repo, session: AsyncSession):
        # Arrange
        create_data = MagicMock()
        expected_result = MagicMock()
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
        update_data = MagicMock()
        expected_result = MagicMock()
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
