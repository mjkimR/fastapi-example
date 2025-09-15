import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from app.core.exceptions.exceptions import UserCantDeleteItselfException
from app.models.users import User
from app.schemas.base import PaginatedList
from app.schemas.users import UserCreate
from app.usecase.users.admin import (
    GetMultiUserUseCase,
    DeleteUserUseCase,
    CreateUserUseCase,
    CreateAdminUseCase,
)


@pytest.fixture
def mock_user_service():
    """Fixture for a mock user service."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Fixture for a mock session."""
    return MagicMock()


@pytest.fixture(autouse=True)
def patch_async_transaction(mocker, mock_session):
    """Fixture to patch AsyncTransaction for all tests in this module."""
    mock_admin_transaction = mocker.patch("app.usecase.users.admin.AsyncTransaction")
    mock_admin_transaction.return_value.__aenter__.return_value = mock_session

    mock_base_transaction = mocker.patch("app.usecase.base.crud.AsyncTransaction")
    mock_base_transaction.return_value.__aenter__.return_value = mock_session


@pytest.mark.asyncio
async def test_get_multi_user_use_case(mock_user_service, mock_session):
    """Test GetMultiUserUseCase."""
    # GIVEN
    users = [User(id=uuid.uuid4(), name=f"User {i}") for i in range(3)]
    expected_paginated_list = PaginatedList(items=users, total_count=len(users), offset=0, limit=10)
    mock_user_service.get_multi.return_value = expected_paginated_list
    use_case = GetMultiUserUseCase(service=mock_user_service)
    params = {"offset": 0, "limit": 10, "order_by": ["-created_at"], "where": "{}"}

    # WHEN
    result = await use_case.execute(**params)

    # THEN
    mock_user_service.get_multi.assert_called_once_with(mock_session, **params)
    assert result == expected_paginated_list


@pytest.mark.asyncio
async def test_delete_user_use_case(mock_user_service, mock_session):
    """Test DeleteUserUseCase successfully deletes another user."""
    # GIVEN
    target_user_id = uuid.uuid4()
    current_user = User(id=uuid.uuid4())
    mock_user_service.delete.return_value = True
    use_case = DeleteUserUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(user_id=target_user_id, current_user=current_user)

    # THEN
    mock_user_service.delete.assert_called_once_with(mock_session, target_user_id)
    assert result is True


@pytest.mark.asyncio
async def test_delete_user_cant_delete_self(mock_user_service):
    """Test DeleteUserUseCase raises exception when user tries to delete self."""
    # GIVEN
    user_id = uuid.uuid4()
    current_user = User(id=user_id)
    use_case = DeleteUserUseCase(service=mock_user_service)

    # WHEN / THEN
    with pytest.raises(UserCantDeleteItselfException):
        await use_case.execute(user_id=user_id, current_user=current_user)
    mock_user_service.delete.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_use_case(mock_user_service, mock_session):
    """Test CreateUserUseCase."""
    # GIVEN
    user_data = UserCreate(
        name="test", surname="user", email="test@example.com", password=SecretStr("password")
    )
    expected_user = User(id=uuid.uuid4(), **user_data.model_dump(exclude={"password"}))
    mock_user_service.create_user.return_value = expected_user
    use_case = CreateUserUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(obj_data=user_data)

    # THEN
    mock_user_service.create_user.assert_called_once_with(mock_session, user_data)
    assert result == expected_user


@pytest.mark.asyncio
async def test_create_admin_use_case(mock_user_service, mock_session):
    """Test CreateAdminUseCase."""
    # GIVEN
    admin_data = UserCreate(
        name="admin", surname="user", email="admin@example.com", password=SecretStr("password")
    )
    expected_admin = User(id=uuid.uuid4(), role=User.Role.ADMIN, **admin_data.model_dump(exclude={"password"}))
    mock_user_service.create_admin.return_value = expected_admin
    use_case = CreateAdminUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(obj_data=admin_data)

    # THEN
    mock_user_service.create_admin.assert_called_once_with(mock_session, admin_data)
    assert result == expected_admin
