"""
Mock data fixtures for unit app_tests.
These are pure mock objects (MagicMock) - NOT real DB fixtures.

For real DB fixtures, see app_tests/fixtures/data/
"""

import datetime
import uuid
from unittest.mock import MagicMock

import pytest

from app.features.auth.models import User
from app.features.memos.models import Memo
from app.features.tags.models import Tag
from app.features.workspaces.models import Workspace

# =============================================================================
# Sample IDs
# =============================================================================


@pytest.fixture
def sample_user_id():
    """Provide a consistent user UUID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def sample_memo_id():
    """Provide a consistent memo UUID for testing."""
    return uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def sample_tag_id():
    """Provide a consistent tag UUID for testing."""
    return uuid.UUID("33333333-3333-3333-3333-333333333333")


@pytest.fixture
def sample_workspace_id():
    """Provide a consistent workspace UUID for testing."""
    return uuid.UUID("44444444-4444-4444-4444-444444444444")


# =============================================================================
# Mock User Models
# =============================================================================


@pytest.fixture
def mock_user(sample_user_id):
    """Create a mock user instance."""
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.name = "Test"
    user.surname = "User"
    user.email = "test@example.com"
    user.role = User.Role.USER
    user.hashed_password = "$2b$12$hashedpassword"
    user.created_at = datetime.datetime.now(datetime.timezone.utc)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return user


@pytest.fixture
def mock_admin_user(sample_user_id):
    """Create a mock admin user instance."""
    user = MagicMock(spec=User)
    user.id = sample_user_id
    user.name = "Admin"
    user.surname = "User"
    user.email = "admin@example.com"
    user.role = User.Role.ADMIN
    user.hashed_password = "$2b$12$hashedpassword"
    user.created_at = datetime.datetime.now(datetime.timezone.utc)
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return user


# =============================================================================
# Mock Workspace Models
# =============================================================================


@pytest.fixture
def mock_workspace(sample_workspace_id, sample_user_id):
    """Create a mock workspace instance."""
    workspace = MagicMock(spec=Workspace)
    workspace.id = sample_workspace_id
    workspace.name = "Test Workspace"
    workspace.created_by = sample_user_id
    workspace.updated_by = None
    workspace.created_at = datetime.datetime.now(datetime.timezone.utc)
    workspace.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return workspace


# =============================================================================
# Mock Memo Models
# =============================================================================


@pytest.fixture
def mock_memo(sample_memo_id, sample_workspace_id, sample_user_id):
    """Create a mock memo instance."""
    memo = MagicMock(spec=Memo)
    memo.id = sample_memo_id
    memo.category = "Test Category"
    memo.title = "Test Title"
    memo.contents = "Test Contents"
    memo.tags = []
    memo.workspace_id = sample_workspace_id
    memo.created_by = sample_user_id
    memo.updated_by = None
    memo.created_at = datetime.datetime.now(datetime.timezone.utc)
    memo.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return memo


# =============================================================================
# Mock Tag Models
# =============================================================================


@pytest.fixture
def mock_tag(sample_tag_id, sample_workspace_id):
    """Create a mock tag instance."""
    tag = MagicMock(spec=Tag)
    tag.id = sample_tag_id
    tag.name = "test-tag"
    tag.workspace_id = sample_workspace_id
    tag.created_at = datetime.datetime.now(datetime.timezone.utc)
    tag.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return tag


@pytest.fixture
def mock_tags(sample_workspace_id):
    """Create multiple mock tags."""
    tags = []
    for _, name in enumerate(["python", "fastapi", "sqlalchemy"]):
        tag = MagicMock(spec=Tag)
        tag.id = uuid.uuid4()
        tag.name = name
        tag.workspace_id = sample_workspace_id
        tags.append(tag)
    return tags
