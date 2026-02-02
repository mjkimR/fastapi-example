"""
Integration app_tests for UserRepository.
Tests CRUD operations with real database connections.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.auth.repos import UserRepository
from app.features.auth.schemas import UserDbCreate, UserDbUpdate


class TestUserRepositoryIntegration:
    """Integration app_tests for UserRepository with real database."""

    @pytest.fixture
    def repo(self) -> UserRepository:
        """Create a UserRepository instance."""
        return UserRepository()

    @pytest.mark.asyncio
    async def test_create_user(self, session: AsyncSession, repo: UserRepository):
        """Should create a new user in the database."""
        user_data = UserDbCreate(
            name="Test",
            surname="User",
            email="newuser@example.com",
            hashed_password="hashed_password_123",
            role=User.Role.USER,
        )

        result = await repo.create(session, user_data)

        assert result is not None
        assert result.id is not None
        assert result.name == user_data.name
        assert result.surname == user_data.surname
        assert result.email == user_data.email
        assert result.role == User.Role.USER

    @pytest.mark.asyncio
    async def test_get_user_by_pk(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should retrieve a user by primary key."""
        result = await repo.get_by_pk(session, pk=regular_user.id)

        assert result is not None
        assert result.id == regular_user.id
        assert result.email == regular_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_pk_not_found(self, session: AsyncSession, repo: UserRepository):
        """Should return None when user not found."""
        non_existent_id = uuid.uuid4()

        result = await repo.get_by_pk(session, pk=non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should retrieve a user by email."""
        result = await repo.get_by_email(session, email=regular_user.email)

        assert result is not None
        assert result.id == regular_user.id
        assert result.email == regular_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, session: AsyncSession, repo: UserRepository):
        """Should return None when email not found."""
        result = await repo.get_by_email(session, email="nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi_users(self, session: AsyncSession, repo: UserRepository, sample_users: list[User]):
        """Should retrieve multiple users with pagination."""
        result = await repo.get_multi(session, offset=0, limit=10)

        assert result.total_count is not None
        assert result.total_count >= len(sample_users)
        assert len(result.items) <= 10

    @pytest.mark.asyncio
    async def test_update_user_by_pk(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should update an existing user."""
        update_data = UserDbUpdate(name="UpdatedName", surname="UpdatedSurname")

        result = await repo.update_by_pk(session, pk=regular_user.id, obj_in=update_data)

        assert result is not None
        assert result.name == "UpdatedName"
        assert result.surname == "UpdatedSurname"

    @pytest.mark.asyncio
    async def test_update_user_partial(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should partially update a user."""
        original_surname = regular_user.surname
        update_data = UserDbUpdate(name="PartialUpdate")

        result = await repo.update_by_pk(session, pk=regular_user.id, obj_in=update_data)

        assert result is not None
        assert result.name == "PartialUpdate"
        assert result.surname == original_surname

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, session: AsyncSession, repo: UserRepository):
        """Should return None when updating non-existent user."""
        non_existent_id = uuid.uuid4()
        update_data = UserDbUpdate(name="Updated")

        result = await repo.update_by_pk(session, pk=non_existent_id, obj_in=update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_user_by_pk(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should delete a user from the database."""
        user_id = regular_user.id

        result = await repo.delete_by_pk(session, pk=user_id)

        assert result is True

        # Verify deletion
        deleted_user = await repo.get_by_pk(session, pk=user_id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, session: AsyncSession, repo: UserRepository):
        """Should return False when deleting non-existent user."""
        non_existent_id = uuid.uuid4()

        result = await repo.delete_by_pk(session, pk=non_existent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_user(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should check if user exists."""
        result = await repo.exists(session, where=User.id == regular_user.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_user_by_email(self, session: AsyncSession, repo: UserRepository, regular_user: User):
        """Should check if user exists by email."""
        result = await repo.exists(session, where=User.email == regular_user.email)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_user_not_found(self, session: AsyncSession, repo: UserRepository):
        """Should return False when user does not exist."""
        non_existent_id = uuid.uuid4()

        result = await repo.exists(session, where=User.id == non_existent_id)

        assert result is False
