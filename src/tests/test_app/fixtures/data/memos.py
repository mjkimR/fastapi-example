"""
Test data fixtures for memos.
"""

import pytest_asyncio
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models import User
from app.features.memos.models import Memo
from app.features.workspaces.models import Workspace


@pytest_asyncio.fixture
async def memo_factory() -> type[SQLAlchemyFactory]:
    class MemoFactory(SQLAlchemyFactory[Memo]):
        pass

    return MemoFactory


@pytest_asyncio.fixture
async def sample_memos(
    session: AsyncSession,
    memo_factory: type[SQLAlchemyFactory],
    single_workspace: Workspace,
    regular_user: User,
) -> list[Memo]:
    """Create sample memos for testing within a workspace."""
    memos = memo_factory.batch(
        size=3,
        workspace_id=single_workspace.id,
        workspace=single_workspace,
        created_by=regular_user.id,
        updated_by=regular_user.id,
    )
    session.add_all(memos)
    await session.flush()
    for memo in memos:
        await session.refresh(memo)
    return memos


@pytest_asyncio.fixture
async def single_memo(
    session: AsyncSession,
    memo_factory: type[SQLAlchemyFactory],
    single_workspace: Workspace,
    regular_user: User,
) -> Memo:
    """Create a single memo for testing within a workspace."""
    memo = memo_factory.build(
        workspace_id=single_workspace.id,
        workspace=single_workspace,
        created_by=regular_user.id,
        updated_by=regular_user.id,
    )
    session.add(memo)
    await session.flush()
    await session.refresh(memo)
    return memo
