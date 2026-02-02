import uuid

import pytest
from httpx import AsyncClient

from tests.test_app.utils import assert_status_code


@pytest.fixture
async def workspace(client: AsyncClient):
    workspace_data = {"name": "Test Workspace"}
    response = await client.post("/api/v1/workspaces", json=workspace_data)
    assert_status_code(response, 201)
    return response.json()


async def test_create_workspace(workspace):
    assert workspace["name"] == "Test Workspace"
    assert "id" in workspace
    assert "created_by" in workspace


async def test_get_workspaces(client: AsyncClient, workspace):
    response = await client.get("/api/v1/workspaces")
    assert_status_code(response, 200)
    data = response.json()
    assert isinstance(data["items"], list)
    assert "total_count" in data
    assert len(data["items"]) > 0


async def test_get_workspace(client: AsyncClient, workspace):
    workspace_id = workspace["id"]
    response = await client.get(f"/api/v1/workspaces/{workspace_id}")
    assert_status_code(response, 200)
    assert response.json()["name"] == workspace["name"]

    non_existent_id = uuid.uuid4()
    response = await client.get(f"/api/v1/workspaces/{non_existent_id}")
    assert_status_code(response, 404)


async def test_update_workspace(client: AsyncClient, workspace):
    workspace_id = workspace["id"]
    update_data = {"name": "Updated Workspace Name"}
    response = await client.put(f"/api/v1/workspaces/{workspace_id}", json=update_data)
    assert_status_code(response, 200)
    assert response.json()["name"] == update_data["name"]

    non_existent_id = uuid.uuid4()
    response = await client.put(f"/api/v1/workspaces/{non_existent_id}", json=update_data)
    assert_status_code(response, 404)


async def test_delete_workspace(client: AsyncClient, workspace):
    workspace_id = workspace["id"]
    response = await client.delete(f"/api/v1/workspaces/{workspace_id}")
    assert_status_code(response, 200)

    # Verify workspace is deleted
    get_response = await client.get(f"/api/v1/workspaces/{workspace_id}")
    assert_status_code(get_response, 404)

    non_existent_id = uuid.uuid4()
    response = await client.delete(f"/api/v1/workspaces/{non_existent_id}")
    assert_status_code(response, 404)
