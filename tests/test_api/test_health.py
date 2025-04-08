from httpx import AsyncClient


async def test_health(client: AsyncClient):
    response = await client.get("/api/health/")
    assert response.status_code == 204
