"""
Test data fixtures for memos.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.memos.models import Memo
from app.features.workspaces.models import Workspace
from app.features.auth.models import User


@pytest_asyncio.fixture
async def sample_memos(
    session: AsyncSession, single_workspace: Workspace, regular_user: User
) -> list[Memo]:
    """Create sample memos for testing within a workspace."""
    memos_data = [
        {
            "category": "General",
            "title": "First Memo",
            "contents": "This is the first test memo content.",
        },
        {
            "category": "Work",
            "title": "Work Todo",
            "contents": "Important work items to complete.",
        },
        {
            "category": "Personal",
            "title": "Shopping List",
            "contents": "Buy groceries: milk, eggs, bread.",
        },
    ]

    memos = [
        Memo(
            **data,
            workspace_id=single_workspace.id,
            created_by=regular_user.id,
        )
        for data in memos_data
    ]
    session.add_all(memos)
    await session.flush()
    for memo in memos:
        await session.refresh(memo)
    return memos


@pytest_asyncio.fixture
async def single_memo(
    session: AsyncSession, single_workspace: Workspace, regular_user: User
) -> Memo:
    """Create a single memo for testing within a workspace."""
    memo = Memo(
        category="Test",
        title="Test Memo",
        contents="This is a test memo.",
        workspace_id=single_workspace.id,
        created_by=regular_user.id,
    )
    session.add(memo)
    await session.flush()
    await session.refresh(memo)
    return memo
