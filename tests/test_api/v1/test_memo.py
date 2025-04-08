import uuid

from httpx import AsyncClient

import pytest


@pytest.fixture
async def memo(client: AsyncClient):
    memo_data = {"category": "General", "title": "Test Memo", "contents": "This is a test memo."}
    response = await client.post("/api/v1/memos/", json=memo_data)
    assert response.status_code == 200
    return response.json()


async def test_create_memo(memo):
    assert memo["category"] == "General"
    assert memo["title"] == "Test Memo"
    assert memo["contents"] == "This is a test memo."
    assert "id" in memo


async def test_get_memos(client: AsyncClient, memo):
    response = await client.get("/api/v1/memos/")
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
    assert "total_count" in response.json()
    assert len(response.json()["data"]) > 0


async def test_get_memo(client: AsyncClient, memo):
    memo_id = memo["id"]
    response = await client.get(f"/api/v1/memos/{memo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == memo["title"]
    assert response.json()["contents"] == memo["contents"]

    non_existent_id = uuid.uuid4()
    response = await client.get(f"/api/v1/memos/{non_existent_id}")
    assert response.status_code == 404


async def test_update_memo(client: AsyncClient, memo):
    memo_id = memo["id"]
    update_data = {"title": "Updated Title", "contents": "Updated Content"}
    response = await client.put(f"/api/v1/memos/{memo_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == update_data["title"]
    assert response.json()["contents"] == update_data["contents"]
    assert response.json()["category"] == memo["category"]

    # Partial update case
    partial_update_data = {"title": "Partially Updated Title"}
    response = await client.put(f"/api/v1/memos/{memo_id}", json=partial_update_data)
    assert response.status_code == 200
    assert response.json()["title"] == partial_update_data["title"]
    assert response.json()["contents"] == update_data["contents"]
    assert response.json()["category"] == memo["category"]

    # Non-existent ID case
    non_existent_id = uuid.uuid4()
    response = await client.put(f"/api/v1/memos/{non_existent_id}", json=update_data)
    assert response.status_code == 404


async def test_delete_memo(client: AsyncClient, memo):
    memo_id = memo["id"]
    response = await client.delete(f"/api/v1/memos/{memo_id}")
    assert response.status_code == 200
    assert "detail" in response.json()

    get_response = await client.get(f"/api/v1/memos/{memo_id}")
    assert get_response.status_code == 404

    non_existent_id = uuid.uuid4()
    response = await client.delete(f"/api/v1/memos/{non_existent_id}")
    assert response.status_code == 404
