"""
E2E (End-to-End) test configuration.
Provides fixtures for API testing with full application stack.

Note: All common fixtures (db, auth, clients, data) are automatically
available from the root app_tests/conftest.py through pytest's fixture discovery.
"""

import pytest
import pytest_asyncio
from sqlalchemy import text

from tests.test_app.fixtures.db import get_base


@pytest_asyncio.fixture(autouse=True)
async def _clean_db_after_e2e_test(async_engine):
    """
    Automatically cleans up the database after each E2E test.

    This is an autouse fixture that applies to all app_tests in the E2E suite.
    It deletes all data from all tables after each test, ensuring test isolation.
    """
    yield

    Base = get_base()
    tables = reversed(Base.metadata.sorted_tables)

    async with async_engine.connect() as conn:
        await conn.begin()
        for table in tables:
            await conn.execute(text(f"DELETE FROM {table.name}"))
        await conn.commit()


@pytest_asyncio.fixture()
async def workspace_via_api(client):
    """Create a workspace via API and return its data."""
    workspace_data = {"name": "E2E Test Workspace"}
    response = await client.post("/api/v1/workspaces", json=workspace_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def memo_via_api(client, workspace_via_api):
    """Create a memo via API and return its data."""
    workspace_id = workspace_via_api["id"]
    memo_data = {
        "category": "General",
        "title": "Test Memo",
        "contents": "This is a test memo.",
    }
    response = await client.post(f"/api/v1/workspaces/{workspace_id}/memos", json=memo_data)
    assert response.status_code == 201
    return response.json()
