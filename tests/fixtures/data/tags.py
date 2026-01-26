"""
Test data fixtures for tags.
"""
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tags.models import Tag
from app.features.workspaces.models import Workspace


@pytest_asyncio.fixture
async def sample_tags(session: AsyncSession, single_workspace: Workspace) -> list[Tag]:
    """Create sample tags for testing within a workspace."""
    tag_names = ["python", "fastapi", "testing"]
    tags = [
        Tag(name=name, workspace_id=single_workspace.id)
        for name in tag_names
    ]
    session.add_all(tags)
    await session.flush()
    for tag in tags:
        await session.refresh(tag)
    return tags


@pytest_asyncio.fixture
async def single_tag(session: AsyncSession, single_workspace: Workspace) -> Tag:
    """Create a single tag for testing within a workspace."""
    tag = Tag(name="test_tag", workspace_id=single_workspace.id)
    session.add(tag)
    await session.flush()
    await session.refresh(tag)
    return tag
