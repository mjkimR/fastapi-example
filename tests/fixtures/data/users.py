"""
Test data fixtures for users.
"""

import uuid

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.models import User


@pytest_asyncio.fixture
async def sample_users(session: AsyncSession, regular_user, admin_user) -> list[User]:
    """Create sample users for testing."""
    return [regular_user, admin_user]


@pytest_asyncio.fixture
async def regular_user(session: AsyncSession) -> User:
    """Create a regular user for testing."""

    user = User(
        id=uuid.uuid4(),
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
async def admin_user(session: AsyncSession) -> User:
    """Create an admin user for testing."""
    user = User(
        id=uuid.uuid4(),
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
