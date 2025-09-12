import asyncio
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_app_settings
from app.core.database import async_session

from app.models.users import User
from app.repos.users import UserRepository
from app.schemas.users import UserCreate
from app.services.users import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_user(
        session: AsyncSession,
        service: UserService,
):
    email = service.settings.FIRST_USER_EMAIL
    password = service.settings.FIRST_USER_PASSWORD.get_secret_value()
    result = await session.execute(select(User).where(User.email == email))
    user: Optional[User] = result.scalars().first()
    if user is None:
        return await service.create_admin(session, UserCreate(
            email=email,
            password=password,
            name="Admin",
            surname="Admin",
        ))


async def main():
    logger.info("Creating initial data")
    service = UserService(
        get_app_settings(),
        repo=UserRepository.get_repo(),
    )
    async with async_session() as session:
        await create_first_user(
            session=session,
            service=service
        )
    logger.info("Initial data created")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
