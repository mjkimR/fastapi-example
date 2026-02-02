import pytest_asyncio
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.workspaces.models import Workspace


@pytest_asyncio.fixture
async def workspace_factory() -> type[SQLAlchemyFactory]:
    class WorkspaceFactory(SQLAlchemyFactory[Workspace]):
        pass

    return WorkspaceFactory


@pytest_asyncio.fixture
async def single_workspace(
    session: AsyncSession,
    workspace_factory: type[SQLAlchemyFactory],
    regular_user: User,
) -> Workspace:
    """
    Fixture for a single workspace, created by the regular user.
    """
    workspace = workspace_factory.build(created_by=regular_user.id, updated_by=regular_user.id)
    session.add(workspace)
    await session.flush()
    await session.refresh(workspace)
    return workspace


@pytest_asyncio.fixture
async def sample_workspaces(
    session: AsyncSession,
    workspace_factory: type[SQLAlchemyFactory],
    regular_user: User,
    admin_user: User,
) -> list[Workspace]:
    """
    Fixture for a list of sample workspaces.
    """
    workspaces = workspace_factory.batch(size=3, created_by=regular_user.id)
    workspaces[1].created_by = admin_user.id

    session.add_all(workspaces)
    await session.flush()
    for ws in workspaces:
        await session.refresh(ws)
    return workspaces
