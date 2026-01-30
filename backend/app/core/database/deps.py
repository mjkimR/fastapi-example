from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.engine import get_session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_maker() as session:
        yield session
