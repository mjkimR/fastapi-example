import asyncio
import logging
from typing import Optional

from app_kit.core.config import get_app_settings
from app_kit.core.database.transaction import AsyncTransaction
from app.features.auth.models import User
from app.features.auth.repos import UserRepository
from app.features.auth.schemas import UserCreate
from app.features.auth.services import UserService
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        return await service.create_admin(
            session,
            UserCreate(
                email=email,
                password=SecretStr(password),
                name="Admin",
                surname="Admin",
            ),
        )


async def main():
    logger.info("Creating initial data")
    service = UserService(
        get_app_settings(),
        repo=UserRepository(),
    )
    async with AsyncTransaction() as session:
        await create_first_user(session=session, service=service)
    logger.info("Initial data created")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
