"""
Test data fixtures for tags.
"""

import pytest_asyncio
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.tags.models import Tag
from app.features.workspaces.models import Workspace


@pytest_asyncio.fixture
async def tag_factory() -> type[SQLAlchemyFactory]:
    class TagFactory(SQLAlchemyFactory[Tag]):
        pass

    return TagFactory


@pytest_asyncio.fixture
async def sample_tags(
    session: AsyncSession,
    tag_factory: type[SQLAlchemyFactory],
    single_workspace: Workspace,
) -> list[Tag]:
    """Create sample tags for testing within a workspace."""
    tags = tag_factory.batch(size=3, workspace_id=single_workspace.id, workspace=single_workspace)
    session.add_all(tags)
    await session.flush()
    for tag in tags:
        await session.refresh(tag)
    return tags


@pytest_asyncio.fixture
async def single_tag(
    session: AsyncSession,
    tag_factory: type[SQLAlchemyFactory],
    single_workspace: Workspace,
) -> Tag:
    """Create a single tag for testing within a workspace."""
    tag = tag_factory.build(workspace_id=single_workspace.id)
    session.add(tag)
    await session.flush()
    await session.refresh(tag)
    return tag
