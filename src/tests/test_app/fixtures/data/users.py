"""
Test data fixtures for users.
"""

import pytest_asyncio
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User


@pytest_asyncio.fixture
async def user_factory() -> type[SQLAlchemyFactory]:
    class UserFactory(SQLAlchemyFactory[User]):
        pass

    return UserFactory


@pytest_asyncio.fixture
async def sample_users(session: AsyncSession, regular_user, admin_user) -> list[User]:
    """Create sample users for testing."""
    return [regular_user, admin_user]


@pytest_asyncio.fixture
async def regular_user(session: AsyncSession, user_factory: type[SQLAlchemyFactory]) -> User:
    """Create a regular user for testing."""

    user = user_factory.build(
        name="Regular",
        surname="User",
        role=User.Role.USER,
        email="regular@example.com",
        hashed_password="hashed_password",
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(session: AsyncSession, user_factory: type[SQLAlchemyFactory]) -> User:
    """Create an admin user for testing."""
    user = user_factory.build(
        name="Admin",
        surname="User",
        role=User.Role.ADMIN,
        email="admin@example.com",
        hashed_password="hashed_admin_password",
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user
