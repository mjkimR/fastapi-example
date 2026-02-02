"""
HTTP Client fixtures for API testing.
"""

from enum import Enum

import orjson
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.token_schemas import Token
from app.main import create_app
from app_base.core.database.deps import get_session


class AsyncClientWithJson(AsyncClient):
    """AsyncClient with custom JSON serialization support."""

    @staticmethod
    def _json_serializer(obj):
        if isinstance(obj, Enum):
            return obj.value
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")

    async def request(self, *args, **kwargs):
        if "json" in kwargs:
            kwargs["content"] = orjson.dumps(kwargs.pop("json"), default=self._json_serializer)
            if kwargs.get("headers") is None:
                kwargs["headers"] = {}
            kwargs["headers"]["Content-Type"] = "application/json"
        return await super().request(*args, **kwargs)


@pytest_asyncio.fixture(name="app")
async def app_fixture(session: AsyncSession):
    """Create FastAPI app with session override."""

    def get_session_override():
        return session

    app = create_app()
    app.dependency_overrides[get_session] = get_session_override
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(name="client")
async def client_fixture(app, admin_token: Token):
    """FastAPI test client with authentication.

    Note: LifespanManager is not used, so lifespan events are not triggered.
    """
    async with AsyncClientWithJson(
        transport=ASGITransport(app=app),
        base_url="http://testserver/",
        follow_redirects=True,
        headers={
            "Authorization": f"Bearer {admin_token.access_token}",
        },
    ) as client:
        yield client


@pytest_asyncio.fixture(name="unauthenticated_client")
async def unauthenticated_client_fixture(app):
    """FastAPI test client without authentication."""
    async with AsyncClientWithJson(
        transport=ASGITransport(app=app),
        base_url="http://testserver/",
        follow_redirects=True,
    ) as client:
        yield client
