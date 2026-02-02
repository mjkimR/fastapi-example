"""
Integration app_tests for UserService.
Tests service layer operations with real database connections.
"""

import pytest
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.exceptions import UserAlreadyExistsException
from app.features.auth.models import User
from app.features.auth.repos import UserRepository
from app.features.auth.schemas import UserCreate, UserUpdate
from app.features.auth.services import UserService
from app_base.config import get_auth_settings


class TestUserServiceIntegration:
    """Integration app_tests for UserService with real database."""

    @pytest.fixture
    def repo(self) -> UserRepository:
        """Create a UserRepository instance."""
        return UserRepository()

    @pytest.fixture
    def service(self, repo: UserRepository) -> UserService:
        """Create a UserService instance."""
        settings = get_auth_settings()
        return UserService(settings=settings, repo=repo)

    @pytest.mark.asyncio
    async def test_create_user(self, session: AsyncSession, service: UserService):
        """Should create a new user through service."""
        user_data = UserCreate(
            name="Service",
            surname="Test",
            email="servicetest@example.com",
            password=SecretStr("password123"),
        )

        result = await service.create_user(session, user_data)

        assert result is not None
        assert result.id is not None
        assert result.name == user_data.name
        assert result.email == user_data.email
        assert result.role == User.Role.USER

    @pytest.mark.asyncio
    async def test_create_admin(self, session: AsyncSession, service: UserService):
        """Should create an admin user through service."""
        user_data = UserCreate(
            name="Admin",
            surname="User",
            email="adminservice@example.com",
            password=SecretStr("adminpassword123"),
        )

        result = await service.create_admin(session, user_data)

        assert result is not None
        assert result.role == User.Role.ADMIN

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, session: AsyncSession, service: UserService, regular_user: User):
        """Should raise exception when creating user with duplicate email."""
        user_data = UserCreate(
            name="Duplicate",
            surname="User",
            email=regular_user.email,
            password=SecretStr("password123"),
        )

        with pytest.raises(UserAlreadyExistsException):
            await service.create_user(session, user_data)

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, session: AsyncSession, service: UserService, regular_user: User):
        """Should retrieve a user by email through service."""
        result = await service.get_by_email(session, email=regular_user.email)

        assert result is not None
        assert result.id == regular_user.id
        assert result.email == regular_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, session: AsyncSession, service: UserService):
        """Should return None when email not found."""
        result = await service.get_by_email(session, email="notfound@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_users(self, session: AsyncSession, service: UserService, sample_users: list[User]):
        """Should retrieve multiple users through service."""
        result = await service.get_multi(session, offset=0, limit=10)

        assert result.total_count is not None
        assert result.total_count >= len(sample_users)
        assert len(result.items) >= 1

    @pytest.mark.asyncio
    async def test_update_user(self, session: AsyncSession, service: UserService):
        """Should update a user through service."""
        # Create user first to avoid fixture password hash issue
        user_data = UserCreate(
            name="ToUpdate",
            surname="User",
            email="updatetest@example.com",
            password=SecretStr("password123"),
        )
        user = await service.create_user(session, user_data)

        # Update with new password (required for update_user to work properly)
        update_data = UserUpdate(
            name="UpdatedServiceName",
            surname="UpdatedSurname",
            password=SecretStr("newpassword"),
        )

        result = await service.update_user(session, update_data, user_id=user.id)

        assert result is not None
        assert result.name == "UpdatedServiceName"
        assert result.surname == "UpdatedSurname"

    @pytest.mark.asyncio
    async def test_delete_user(self, session: AsyncSession, service: UserService, regular_user: User):
        """Should delete a user through service."""
        result = await service.delete(session, obj_id=regular_user.id)

        assert result.success is True

        # Verify deletion
        deleted_user = await service.get_by_email(session, email=regular_user.email)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_authenticate_valid_credentials(self, session: AsyncSession, service: UserService):
        """Should authenticate user with valid credentials."""
        # First create a user with known password
        password = "testpassword123"
        user_data = UserCreate(
            name="Auth",
            surname="Test",
            email="authtest@example.com",
            password=SecretStr(password),
        )
        created_user = await service.create_user(session, user_data)

        # Authenticate
        result = await service.authenticate(session, email=created_user.email, password=password)

        assert result is not None
        assert result.id == created_user.id

    @pytest.mark.asyncio
    async def test_authenticate_invalid_password(self, session: AsyncSession, service: UserService):
        """Should return None for invalid password."""
        # First create a user
        user_data = UserCreate(
            name="Auth",
            surname="Invalid",
            email="authinvalid@example.com",
            password=SecretStr("correctpassword"),
        )
        await service.create_user(session, user_data)

        # Try to authenticate with wrong password
        result = await service.authenticate(session, email="authinvalid@example.com", password="wrongpassword")

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user(self, session: AsyncSession, service: UserService):
        """Should return None for nonexistent user."""
        result = await service.authenticate(session, email="nonexistent@example.com", password="anypassword")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_access_token(self, session: AsyncSession, service: UserService):
        """Should create a valid access token."""
        # Create a user
        user_data = UserCreate(
            name="Token",
            surname="Test",
            email="tokentest@example.com",
            password=SecretStr("password123"),
        )
        user = await service.create_user(session, user_data)

        # Create token
        token = service.create_access_token(user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_password_hashing(self, service: UserService):
        """Should hash and verify passwords correctly."""
        password = "testpassword123"

        hashed = service.get_password_hash(password)

        assert hashed != password
        assert service.is_valid_password(password, hashed)
        assert not service.is_valid_password("wrongpassword", hashed)
