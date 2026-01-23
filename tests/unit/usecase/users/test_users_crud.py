import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions.exceptions import PermissionDeniedException
from app.models.users import User
from app.schemas.users import UserUpdate
from app.usecase.users.crud import GetUserUseCase, UpdateUserUseCase


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
    mock_async_transaction = mocker.patch("app.usecase.users.crud.AsyncTransaction")
    mock_async_transaction.return_value.__aenter__.return_value = mock_session
    return mock_async_transaction


# --- GetUserUseCase Tests ---

@pytest.mark.asyncio
async def test_get_user_self(mock_user_service):
    """Test GetUserUseCase when a user requests their own data."""
    # GIVEN
    user_id = uuid.uuid4()
    current_user = User(id=user_id, role=User.Role.USER)
    use_case = GetUserUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(user_id=user_id, current_user=current_user)

    # THEN
    assert result == current_user
    mock_user_service.get.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_by_admin(mock_user_service, mock_session):
    """Test GetUserUseCase when an admin requests another user's data."""
    # GIVEN
    target_user_id = uuid.uuid4()
    admin_user = User(id=uuid.uuid4(), role=User.Role.ADMIN)
    expected_user = User(id=target_user_id, name="test")
    mock_user_service.get.return_value = expected_user
    use_case = GetUserUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(user_id=target_user_id, current_user=admin_user)

    # THEN
    mock_user_service.get.assert_called_once_with(mock_session, target_user_id, context=None)
    assert result == expected_user


@pytest.mark.asyncio
async def test_get_user_permission_denied(mock_user_service):
    """Test GetUserUseCase when a non-admin user requests another user's data."""
    # GIVEN
    target_user_id = uuid.uuid4()
    current_user = User(id=uuid.uuid4(), role=User.Role.USER)
    use_case = GetUserUseCase(service=mock_user_service)

    # WHEN / THEN
    with pytest.raises(PermissionDeniedException) as exc_info:
        await use_case.execute(user_id=target_user_id, current_user=current_user)
    assert exc_info.value.status_code == 403
    mock_user_service.get.assert_not_called()


# --- UpdateUserUseCase Tests ---

@pytest.mark.asyncio
async def test_update_user_self(mock_user_service):
    """Test UpdateUserUseCase when a user updates their own data."""
    # GIVEN
    user_id = uuid.uuid4()
    current_user = User(id=user_id, role=User.Role.USER)
    update_data = UserUpdate(name="Updated Name")
    use_case = UpdateUserUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(obj_data=update_data, user_id=user_id, current_user=current_user)

    # THEN
    assert result == current_user
    mock_user_service.update_user.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_by_admin(mock_user_service, mock_session):
    """Test UpdateUserUseCase when an admin updates another user's data."""
    # GIVEN
    target_user_id = uuid.uuid4()
    admin_user = User(id=uuid.uuid4(), role=User.Role.ADMIN)
    update_data = UserUpdate(name="Updated Name")
    expected_user = User(id=target_user_id, name="Updated Name")
    mock_user_service.update_user.return_value = expected_user
    use_case = UpdateUserUseCase(service=mock_user_service)

    # WHEN
    result = await use_case.execute(obj_data=update_data, user_id=target_user_id, current_user=admin_user)

    # THEN
    mock_user_service.update_user.assert_called_once_with(mock_session, update_data, target_user_id)
    assert result == expected_user


@pytest.mark.asyncio
async def test_update_user_permission_denied(mock_user_service):
    """Test UpdateUserUseCase when a non-admin user tries to update another user's data."""
    # GIVEN
    target_user_id = uuid.uuid4()
    current_user = User(id=uuid.uuid4(), role=User.Role.USER)
    update_data = UserUpdate(name="Updated Name")
    use_case = UpdateUserUseCase(service=mock_user_service)

    # WHEN / THEN
    with pytest.raises(PermissionDeniedException) as exc_info:
        await use_case.execute(obj_data=update_data, user_id=target_user_id, current_user=current_user)
    assert exc_info.value.status_code == 403
    mock_user_service.update_user.assert_not_called()
