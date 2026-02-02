import uuid

import pytest
from httpx import AsyncClient

from tests.test_app.utils import assert_status_code


@pytest.fixture
async def memo(client: AsyncClient, workspace_via_api: dict):
    workspace_id = workspace_via_api["id"]
    memo_data = {
        "category": "General",
        "title": "Test Memo",
        "contents": "This is a test memo.",
        "tags": [],
    }
    response = await client.post(f"/api/v1/workspaces/{workspace_id}/memos", json=memo_data)
    assert_status_code(response, 201)
    return response.json()


async def test_create_memo(memo):
    assert memo["category"] == "General"
    assert memo["title"] == "Test Memo"
    assert memo["contents"] == "This is a test memo."
    assert "id" in memo


async def test_get_memos(client: AsyncClient, memo, workspace_via_api: dict):
    workspace_id = workspace_via_api["id"]
    response = await client.get(f"/api/v1/workspaces/{workspace_id}/memos")
    assert_status_code(response, 200)
    data = response.json()
    assert isinstance(data["items"], list)
    assert "total_count" in data
    assert len(data["items"]) > 0


async def test_get_memo(client: AsyncClient, memo, workspace_via_api: dict):
    workspace_id = workspace_via_api["id"]
    memo_id = memo["id"]
    response = await client.get(f"/api/v1/workspaces/{workspace_id}/memos/{memo_id}")
    assert_status_code(response, 200)
    assert response.json()["title"] == memo["title"]
    assert response.json()["contents"] == memo["contents"]

    non_existent_id = uuid.uuid4()
    response = await client.get(f"/api/v1/workspaces/{workspace_id}/memos/{non_existent_id}")
    assert_status_code(response, 404)


async def test_update_memo(client: AsyncClient, memo, workspace_via_api: dict):
    workspace_id = workspace_via_api["id"]
    memo_id = memo["id"]
    update_data = {"title": "Updated Title", "contents": "Updated Content"}
    response = await client.put(f"/api/v1/workspaces/{workspace_id}/memos/{memo_id}", json=update_data)
    assert_status_code(response, 200)
    assert response.json()["title"] == update_data["title"]
    assert response.json()["contents"] == update_data["contents"]
    assert response.json()["category"] == memo["category"]

    # Partial update case
    partial_update_data = {"title": "Partially Updated Title"}
    response = await client.put(f"/api/v1/workspaces/{workspace_id}/memos/{memo_id}", json=partial_update_data)
    assert_status_code(response, 200)
    assert response.json()["title"] == partial_update_data["title"]
    assert response.json()["contents"] == update_data["contents"]
    assert response.json()["category"] == memo["category"]

    # Non-existent ID case
    non_existent_id = uuid.uuid4()
    response = await client.put(f"/api/v1/workspaces/{workspace_id}/memos/{non_existent_id}", json=update_data)
    assert_status_code(response, 404)


async def test_delete_memo(client: AsyncClient, memo, workspace_via_api: dict):
    workspace_id = workspace_via_api["id"]
    memo_id = memo["id"]
    response = await client.delete(f"/api/v1/workspaces/{workspace_id}/memos/{memo_id}")
    assert_status_code(response, 200)

    # Verify memo is deleted
    get_response = await client.get(f"/api/v1/workspaces/{workspace_id}/memos/{memo_id}")
    assert_status_code(get_response, 404)

    # Non-existent ID case
    non_existent_id = uuid.uuid4()
    response = await client.delete(f"/api/v1/workspaces/{workspace_id}/memos/{non_existent_id}")
    assert_status_code(response, 404)
