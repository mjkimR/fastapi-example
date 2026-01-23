import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.base.schemas import PaginatedList
from backend.app.base.services.base import (
    BaseCRUDServiceMixin, BaseContextKwargs
)
from backend.app.base.repos.base import BaseRepository


class MockCRUDService(BaseCRUDServiceMixin):
    """Test service using mixin structure."""
    def __init__(self, repo):
        self.repo = repo
        self.context_model = BaseContextKwargs


class TestBaseCRUDServiceMixin:

    @pytest.fixture
    def mock_repo(self):
        repo = AsyncMock(spec=BaseRepository)
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        return MockCRUDService(repo=mock_repo)

    @pytest.mark.asyncio
    async def test_get(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        expected_result = MagicMock()
        mock_repo.get_by_pk.return_value = expected_result

        # Act
        result = await service.get(session, test_id)

        # Assert
        mock_repo.get_by_pk.assert_awaited_once_with(session, pk=test_id)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_multi(self, service, mock_repo, session: AsyncSession):
        # Arrange
        expected_result = MagicMock(spec=PaginatedList)
        mock_repo.get_multi.return_value = expected_result
        offset, limit = 10, 20

        # Act
        result = await service.get_multi(session, offset=offset, limit=limit)

        # Assert
        mock_repo.get_multi.assert_awaited_once_with(session, offset=offset, limit=limit, where=[], order_by=None)
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
        mock_repo.create.assert_awaited_once_with(session, obj_in=create_data)
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        update_data = MagicMock()
        expected_result = MagicMock()
        mock_repo.update_by_pk.return_value = expected_result

        # Act
        result = await service.update(session, test_id, update_data)

        # Assert
        mock_repo.update_by_pk.assert_awaited_once_with(
            session, pk=test_id, obj_in=update_data
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_delete(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        mock_repo.delete_by_pk.return_value = True

        # Act
        result = await service.delete(session, test_id)

        # Assert
        mock_repo.delete_by_pk.assert_awaited_once_with(session, pk=test_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_failure(self, service, mock_repo, session: AsyncSession):
        # Arrange
        test_id = uuid.uuid4()
        mock_repo.delete_by_pk.return_value = False

        # Act
        result = await service.delete(session, test_id)

        # Assert
        mock_repo.delete_by_pk.assert_awaited_once_with(session, pk=test_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_create_with_context(self, service, mock_repo, session: AsyncSession):
        # Arrange
        create_data = MagicMock()
        expected_result = MagicMock()
        mock_repo.create.return_value = expected_result
        context = {}

        # Act
        result = await service.create(session, create_data, context=context)

        # Assert
        mock_repo.create.assert_awaited_once_with(session, obj_in=create_data)
        assert result == expected_result
