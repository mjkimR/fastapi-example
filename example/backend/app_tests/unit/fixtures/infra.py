"""
Mock infrastructure fixtures for unit app_tests.
Session, settings, and other infrastructure mocks.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

# =============================================================================
# Mock Session
# =============================================================================


@pytest.fixture
def mock_async_session():
    """Create a fully mocked async session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    session.get = AsyncMock()
    return session


# =============================================================================
# Mock Settings
# =============================================================================


@pytest.fixture
def mock_settings():
    """Create mock application settings."""
    settings = MagicMock()
    settings.SECRET_KEY = SecretStr("test-secret-key-for-testing-purposes-only")
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    return settings
