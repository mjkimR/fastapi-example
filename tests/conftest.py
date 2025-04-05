import logging
from enum import Enum

import orjson
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from httpx import AsyncClient, ASGITransport
import pytest_asyncio

from core.database import get_session
from main import create_app


@pytest.fixture(name="session")
def session_fixture():
    """Create a new database session for testing with SQLite."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def set_httpx_logger():
    """Set httpx logger to WARNING level."""
    logging.getLogger("httpx").setLevel(logging.WARNING)


class AsyncClientWithJson(AsyncClient):
    @staticmethod
    def _json_serializer(obj):
        if isinstance(obj, Enum):
            return obj.value
        # if isinstance(obj, pydantic.BaseModel):
        #     return obj.model_dump()
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")

    async def request(self, *args, **kwargs):
        if 'json' in kwargs:
            kwargs['content'] = orjson.dumps(kwargs.pop('json'), default=self._json_serializer)
            if kwargs['headers'] is None:
                kwargs['headers'] = {}
            kwargs['headers']['Content-Type'] = 'application/json'
        return await super().request(*args, **kwargs)


@pytest_asyncio.fixture(name="client")
async def client_fixture(session: Session, set_httpx_logger):
    """FastAPI test client (without LifespanManager).

    - LifespanManager is not used: lifespan events are not triggered.
    """

    def get_session_override():
        return session

    app = create_app()
    app.dependency_overrides[get_session] = get_session_override

    async with (
        AsyncClientWithJson(
            transport=ASGITransport(app=app),
            base_url="http://testserver/",
        ) as client,
    ):
        yield client

    app.dependency_overrides.clear()
