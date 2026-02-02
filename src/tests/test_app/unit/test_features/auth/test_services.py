from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from app.features.auth.exceptions import UserAlreadyExistsException
from app.features.auth.models import User
from app.features.auth.schemas import UserCreate
from app.features.auth.services import UserService


class TestUserServicePasswordHashing:
    """Tests for password hashing functionality."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    def test_get_password_hash_returns_hashed_string(self, user_service):
        """Should return hashed password string."""
        password = "test_password123"
        hashed = user_service.get_password_hash(password)

        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_is_valid_password_returns_true_for_correct_password(self, user_service):
        """Should return True for correct password."""
        password = "test_password123"
        hashed = user_service.get_password_hash(password)

        result = user_service.is_valid_password(password, hashed)

        assert result is True

    def test_is_valid_password_returns_false_for_incorrect_password(self, user_service):
        """Should return False for incorrect password."""
        password = "test_password123"
        hashed = user_service.get_password_hash(password)

        result = user_service.is_valid_password("wrong_password", hashed)

        assert result is False


class TestUserServiceValidation:
    """Tests for email validation."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    @pytest.mark.asyncio
    async def test_validate_email_exists_raises_when_exists(self, user_service, mock_async_session):
        """Should raise UserAlreadyExistsException when email exists."""
        user_service.repo.exists.return_value = True

        with pytest.raises(UserAlreadyExistsException):
            await user_service.validate_email_exists(mock_async_session, "existing@example.com")

    @pytest.mark.asyncio
    async def test_validate_email_exists_passes_when_not_exists(self, user_service, mock_async_session):
        """Should not raise when email doesn't exist."""
        user_service.repo.exists.return_value = False

        # Should not raise
        await user_service.validate_email_exists(mock_async_session, "new@example.com")


class TestUserServiceCreateUser:
    """Tests for create user functionality."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    @pytest.mark.asyncio
    async def test_create_user_sets_user_role(self, user_service, mock_async_session, mock_user):
        """Should create user with USER role."""
        user_service.repo.exists.return_value = False
        user_service.repo.create.return_value = mock_user

        user_data = UserCreate(
            name="Test",
            surname="User",
            email="test@example.com",
            password=SecretStr("password123"),
        )

        await user_service.create_user(mock_async_session, user_data)

        user_service.repo.create.assert_called_once()
        call_args = user_service.repo.create.call_args
        created_data = call_args[0][1]  # Second positional arg is user_data
        assert created_data.role == User.Role.USER

    @pytest.mark.asyncio
    async def test_create_user_hashes_password(self, user_service, mock_async_session, mock_user):
        """Should hash password before storing."""
        user_service.repo.exists.return_value = False
        user_service.repo.create.return_value = mock_user

        user_data = UserCreate(
            name="Test",
            surname="User",
            email="test@example.com",
            password=SecretStr("password123"),
        )

        await user_service.create_user(mock_async_session, user_data)

        call_args = user_service.repo.create.call_args
        created_data = call_args[0][1]
        assert created_data.hashed_password.startswith("$2b$")

    @pytest.mark.asyncio
    async def test_create_user_raises_when_email_exists(self, user_service, mock_async_session):
        """Should raise when email already exists."""
        user_service.repo.exists.return_value = True

        user_data = UserCreate(
            name="Test",
            surname="User",
            email="existing@example.com",
            password=SecretStr("password123"),
        )

        with pytest.raises(UserAlreadyExistsException):
            await user_service.create_user(mock_async_session, user_data)


class TestUserServiceCreateAdmin:
    """Tests for create admin functionality."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    @pytest.mark.asyncio
    async def test_create_admin_sets_admin_role(self, user_service, mock_async_session, mock_admin_user):
        """Should create user with ADMIN role."""
        user_service.repo.exists.return_value = False
        user_service.repo.create.return_value = mock_admin_user

        user_data = UserCreate(
            name="Admin",
            surname="User",
            email="admin@example.com",
            password=SecretStr("password123"),
        )

        await user_service.create_admin(mock_async_session, user_data)

        call_args = user_service.repo.create.call_args
        created_data = call_args[0][1]
        assert created_data.role == User.Role.ADMIN


class TestUserServiceAuthenticate:
    """Tests for authentication functionality."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    @pytest.mark.asyncio
    async def test_authenticate_returns_user_for_valid_credentials(self, user_service, mock_async_session):
        """Should return user when credentials are valid."""
        password = "password123"
        hashed = user_service.get_password_hash(password)

        mock_user = MagicMock()
        mock_user.hashed_password = hashed
        user_service.repo.get_by_email.return_value = mock_user

        result = await user_service.authenticate(mock_async_session, "test@example.com", password)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_returns_none_for_invalid_password(self, user_service, mock_async_session):
        """Should return None when password is invalid."""
        hashed = user_service.get_password_hash("correct_password")

        mock_user = MagicMock()
        mock_user.hashed_password = hashed
        user_service.repo.get_by_email.return_value = mock_user

        result = await user_service.authenticate(mock_async_session, "test@example.com", "wrong_password")

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_returns_none_for_nonexistent_user(self, user_service, mock_async_session):
        """Should return None when user doesn't exist."""
        user_service.repo.get_by_email.return_value = None

        result = await user_service.authenticate(mock_async_session, "nonexistent@example.com", "password")

        assert result is None


class TestUserServiceToken:
    """Tests for token functionality."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    def test_create_access_token_returns_jwt_string(self, user_service, mock_user):
        """Should return JWT token string."""
        token = user_service.create_access_token(mock_user)

        assert isinstance(token, str)
        # JWT has 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3


class TestUserServiceGetByEmail:
    """Tests for get_by_email functionality."""

    @pytest.fixture
    def user_service(self, mock_settings):
        """Create UserService with mocked dependencies."""
        repo = AsyncMock()
        return UserService(settings=mock_settings, repo=repo)

    @pytest.mark.asyncio
    async def test_get_by_email_returns_user(self, user_service, mock_async_session, mock_user):
        """Should return user when found."""
        user_service.repo.get_by_email.return_value = mock_user

        result = await user_service.get_by_email(mock_async_session, "test@example.com")

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_by_email_returns_none_when_not_found(self, user_service, mock_async_session):
        """Should return None when user not found."""
        user_service.repo.get_by_email.return_value = None

        result = await user_service.get_by_email(mock_async_session, "nonexistent@example.com")

        assert result is None
