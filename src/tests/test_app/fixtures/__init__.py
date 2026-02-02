"""
Centralized fixtures package.
Import all fixtures from this package for easy access.
"""

from tests.test_app.fixtures.auth import (
    admin_headers,
    admin_token,
    admin_user,
    user_service,
)
from tests.test_app.fixtures.clients import (
    AsyncClientWithJson,
    app_fixture,
    client_fixture,
    unauthenticated_client_fixture,
)
from tests.test_app.fixtures.db import (
    async_engine,
    event_loop_policy,
    inspect_session,
    session_fixture,
    session_maker_fixture,
)

__all__ = [
    # Database fixtures
    "event_loop_policy",
    "async_engine",
    "session_maker_fixture",
    "session_fixture",
    "inspect_session",
    # Client fixtures
    "AsyncClientWithJson",
    "app_fixture",
    "client_fixture",
    "unauthenticated_client_fixture",
    # Auth fixtures
    "user_service",
    "admin_user",
    "admin_token",
    "admin_headers",
]
