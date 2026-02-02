"""
Authentication fixtures for testing.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.repos import UserRepository
from app.features.auth.services import UserService
from app.features.auth.token_schemas import Token
from app_base.config import get_auth_settings
from init_data.initial_data import create_first_user


@pytest_asyncio.fixture
async def user_service() -> UserService:
    """Create a user service instance."""
    return UserService(
        settings=get_auth_settings(),
        repo=UserRepository(),
    )


@pytest_asyncio.fixture
async def admin_user(session: AsyncSession, user_service: UserService):
    """Create or get an admin user for testing."""
    from sqlalchemy import select

    from app.features.auth.models import User

    user = await create_first_user(session, user_service)
    if user is None:
        # User already exists, fetch it
        email = user_service.settings.FIRST_USER_EMAIL
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
    if user is None:
        raise ValueError("Admin user creation/fetch failed")
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user, user_service: UserService) -> Token:
    """Create an admin token for the first user."""
    return Token(
        access_token=user_service.create_access_token(admin_user),
        token_type="bearer",
    )


@pytest_asyncio.fixture
async def admin_headers(admin_token: Token) -> dict[str, str]:
    """Create headers with admin token."""
    return {
        "Authorization": f"Bearer {admin_token.access_token}",
        "Content-Type": "application/json",
    }
