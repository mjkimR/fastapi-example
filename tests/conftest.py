from app.core.config import get_app_settings

import logging
from enum import Enum

import orjson
import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps.session import get_session
from app.core.transaction import AsyncTransaction
from app.main import create_app
from app.models.base import Base
from app.repos.users import UserRepository
from app.schemas.token import Token
from app.services.users import UserService
from init_data.initial_data import create_first_user


@pytest.fixture(name="session_maker")
async def session_maker_fixture(monkeypatch: pytest.MonkeyPatch):
    """Create a new database session_maker for testing with SQLite."""
    async_engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Use async method to create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    monkeypatch.setattr(AsyncTransaction, "DEFAULT_SESSION_MAKER", session_maker)

    yield session_maker
    await async_engine.dispose()


@pytest.fixture(name="session")
async def session_fixture(session_maker):
    """Create a new database session for testing with SQLite."""
    async with session_maker() as session:
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


@pytest_asyncio.fixture
async def admin_token(session: AsyncSession) -> Token:
    """Create an admin token for the first user."""
    service = UserService(
        settings=get_app_settings(),
        repo=UserRepository(),
    )
    user = await create_first_user(session, service)
    if user is None:
        raise ValueError("Super admin user creation failed")

    return Token(
        access_token=service.create_access_token(user),
        token_type="bearer",
    )


@pytest_asyncio.fixture(name="client")
async def client_fixture(session_maker: async_sessionmaker, session: AsyncSession, set_httpx_logger, admin_token):
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
            headers={
                "Authorization": f"Bearer {admin_token.access_token}",
            },
        ) as client,
    ):
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_header(admin_token: Token) -> dict[str, str]:
    """Create headers with admin token."""
    return {
        "Authorization": f"Bearer {admin_token.access_token}",
        "Content-Type": "application/json",
    }
