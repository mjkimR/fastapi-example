import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.workspaces.models import Workspace


@pytest_asyncio.fixture
async def single_workspace(session: AsyncSession, regular_user: User) -> Workspace:
    """
    Fixture for a single workspace, created by the regular user.
    """
    workspace = Workspace(name="Test Workspace", created_by=regular_user.id)
    session.add(workspace)
    await session.flush()
    await session.refresh(workspace)
    return workspace


@pytest_asyncio.fixture
async def sample_workspaces(session: AsyncSession, regular_user: User, admin_user: User) -> list[Workspace]:
    """
    Fixture for a list of sample workspaces.
    """
    workspaces = [
        Workspace(name="Workspace 1", created_by=regular_user.id),
        Workspace(name="Workspace 2", created_by=admin_user.id),
        Workspace(name="Workspace 3", created_by=regular_user.id),
    ]
    session.add_all(workspaces)
    await session.flush()
    for ws in workspaces:
        await session.refresh(ws)
    return workspaces
