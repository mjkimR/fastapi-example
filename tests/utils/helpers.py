"""
Common test helper functions.
"""

import uuid
from typing import TypeVar

T = TypeVar("T")


def random_email() -> str:
    """Generate a random email for testing."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def random_string(prefix: str = "test") -> str:
    """Generate a random string for testing."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def create_and_get(client, endpoint: str, data: dict) -> dict:
    """Create a resource via API and return the response data."""
    response = await client.post(endpoint, json=data)
    assert response.status_code == 201, f"Create failed: {response.text}"
    return response.json()


async def cleanup_resource(client, endpoint: str, resource_id: str):
    """Delete a resource via API."""
    await client.delete(f"{endpoint}/{resource_id}")
