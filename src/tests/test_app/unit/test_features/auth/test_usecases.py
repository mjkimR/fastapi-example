import uuid
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr

from app.features.auth.exceptions import (
    PermissionDeniedException,
    UserCantDeleteItselfException,
)
from app.features.auth.models import User
from app.features.auth.schemas import UserCreate, UserUpdate
from app.features.auth.usecases.admin import (
    CreateAdminUseCase,
    CreateUserUseCase,
    DeleteUserUseCase,
    GetMultiUserUseCase,
)
from app.features.auth.usecases.crud import GetUserUseCase, UpdateUserUseCase
from app_base.base.schemas.paginated import PaginatedList


class TestGetUserUseCase:
    """Tests for GetUserUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return GetUserUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_current_user_when_same_id(self, use_case, mock_user, sample_user_id):
        """Should return current user when requesting own data."""
        mock_user.id = sample_user_id

        result = await use_case.execute(sample_user_id, current_user=mock_user)

        assert result == mock_user
        use_case.service.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_raises_when_non_admin_requests_other_user(self, use_case, mock_user, sample_user_id):
        """Should raise PermissionDeniedException when non-admin requests other user."""
        mock_user.id = uuid.uuid4()  # Different ID
        mock_user.role = User.Role.USER

        with pytest.raises(PermissionDeniedException):
            await use_case.execute(sample_user_id, current_user=mock_user)

    @pytest.mark.asyncio
    async def test_execute_returns_user_when_admin_requests(self, use_case, mock_admin_user, mock_user, sample_user_id):
        """Should return user when admin requests other user."""
        mock_admin_user.id = uuid.uuid4()  # Different ID
        mock_admin_user.role = User.Role.ADMIN
        use_case.service.get.return_value = mock_user

        with patch("app.features.auth.usecases.crud.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(sample_user_id, current_user=mock_admin_user)

        assert result == mock_user


class TestUpdateUserUseCase:
    """Tests for UpdateUserUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return UpdateUserUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_current_user_when_same_id(self, use_case, mock_user, sample_user_id):
        """Should return current user when updating own data."""
        mock_user.id = sample_user_id
        update_data = UserUpdate(name="Updated Name")

        result = await use_case.execute(update_data, sample_user_id, current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_execute_raises_when_non_admin_updates_other_user(self, use_case, mock_user, sample_user_id):
        """Should raise PermissionDeniedException when non-admin updates other user."""
        mock_user.id = uuid.uuid4()  # Different ID
        mock_user.role = User.Role.USER
        update_data = UserUpdate(name="Updated Name")

        with pytest.raises(PermissionDeniedException):
            await use_case.execute(update_data, sample_user_id, current_user=mock_user)


class TestDeleteUserUseCase:
    """Tests for DeleteUserUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return DeleteUserUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_raises_when_deleting_self(self, use_case, mock_user, sample_user_id):
        """Should raise UserCantDeleteItselfException when deleting self."""
        mock_user.id = sample_user_id

        with pytest.raises(UserCantDeleteItselfException):
            await use_case.execute(sample_user_id, current_user=mock_user)

    @pytest.mark.asyncio
    async def test_execute_returns_true_when_deleted(self, use_case, mock_user, sample_user_id):
        """Should return True when user deleted."""
        mock_user.id = uuid.uuid4()  # Different ID
        use_case.service.delete.return_value = True

        with patch("app.features.auth.usecases.admin.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(sample_user_id, current_user=mock_user)

        assert result is True


class TestCreateUserUseCase:
    """Tests for CreateUserUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return CreateUserUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_creates_user(self, use_case, mock_user):
        """Should create user via service."""
        use_case.service.create_user.return_value = mock_user
        user_data = UserCreate(
            name="Test",
            surname="User",
            email="test@example.com",
            password=SecretStr("password123"),
        )

        with patch("app.features.auth.usecases.admin.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(user_data)

        assert result == mock_user
        use_case.service.create_user.assert_called_once()


class TestCreateAdminUseCase:
    """Tests for CreateAdminUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return CreateAdminUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_creates_admin(self, use_case, mock_admin_user):
        """Should create admin via service."""
        use_case.service.create_admin.return_value = mock_admin_user
        user_data = UserCreate(
            name="Admin",
            surname="User",
            email="admin@example.com",
            password=SecretStr("password123"),
        )

        with patch("app.features.auth.usecases.admin.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(user_data)

        assert result == mock_admin_user
        use_case.service.create_admin.assert_called_once()


class TestGetMultiUserUseCase:
    """Tests for GetMultiUserUseCase."""

    @pytest.fixture
    def use_case(self):
        """Create use case with mocked service."""
        service = AsyncMock()
        return GetMultiUserUseCase(service=service)

    @pytest.mark.asyncio
    async def test_execute_returns_paginated_users(self, use_case, mock_user):
        """Should return paginated list of users."""
        paginated = PaginatedList(items=[mock_user], total_count=1, offset=0, limit=10)
        use_case.service.get_multi.return_value = paginated

        with patch("app.features.auth.usecases.admin.AsyncTransaction") as mock_tx:
            mock_tx.return_value.__aenter__.return_value = AsyncMock()
            result = await use_case.execute(offset=0, limit=10)

        assert result == paginated
