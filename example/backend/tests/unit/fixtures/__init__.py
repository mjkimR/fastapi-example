"""
Unit test fixtures package.
Provides mock objects for isolated unit testing.
"""

from example.backend.tests.unit.fixtures.data import (
    mock_admin_user,
    mock_memo,
    mock_tag,
    mock_tags,
    mock_user,
    sample_memo_id,
    sample_tag_id,
    sample_user_id,
)
from example.backend.tests.unit.fixtures.infra import (
    mock_async_session,
    mock_settings,
)

__all__ = [
    # Sample IDs
    "sample_user_id",
    "sample_memo_id",
    "sample_tag_id",
    # Mock models
    "mock_user",
    "mock_admin_user",
    "mock_memo",
    "mock_tag",
    "mock_tags",
    # Infrastructure mocks
    "mock_async_session",
    "mock_settings",
]
