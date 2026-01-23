from typing import Annotated, Union
from uuid import UUID

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

from app.core.config import get_app_settings, AppSettings
from app.core.exceptions.exceptions import UserAlreadyExistsException
from app.features.auth.models import User
from app.features.auth.repos import UserRepository
from app.features.auth.schemas import UserCreate, UserUpdate, UserDbCreate, UserDbUpdate
from app.base.services.base import (
    BaseGetServiceMixin,
    BaseGetMultiServiceMixin,
    BaseDeleteServiceMixin, BaseContextKwargs,
)

"""
* https://github.com/ViktorViskov/fastapi-mvc/blob/main/app/utils/bcrypt_hashing.py
* https://github.com/ViktorViskov/fastapi-mvc/blob/main/app/utils/sha256_hashing.py
* https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/core/security.py
* https://github.com/Kludex/fastapi-microservices/blob/main/users/app/core/security.py
"""


class UserService(
    BaseGetServiceMixin[UserRepository, User, BaseContextKwargs],
    BaseGetMultiServiceMixin[UserRepository, User, BaseContextKwargs],
    BaseDeleteServiceMixin[UserRepository, User, BaseContextKwargs],
):
    """Service class for handling user-related operations."""

    ALGORITHM = "HS256"

    def __init__(
            self,
            settings: Annotated[AppSettings, Depends(get_app_settings)],
            repo: Annotated[UserRepository, Depends()],
    ):
        self.settings = settings
        self.repo = repo
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def validate_email_exists(self, session: AsyncSession, email: Union[str, EmailStr]) -> None:
        """Validate if an email exists."""
        if await self.repo.exists(session, where=User.email == str(email)):
            raise UserAlreadyExistsException()

    async def create_user(self, session: AsyncSession, obj_data: UserCreate) -> User:
        """Create a new user."""
        await self.validate_email_exists(session, obj_data.email)
        user_data = UserDbCreate(
            **obj_data.model_dump(),
            role=User.Role.USER,
            hashed_password=self.get_password_hash(
                obj_data.password.get_secret_value()
            ),
        )
        return await self.repo.create(session, user_data)

    async def create_admin(self, session: AsyncSession, obj_data: UserCreate) -> User:
        """Create a new admin user."""
        await self.validate_email_exists(session, obj_data.email)
        user_data = UserDbCreate(
            **obj_data.model_dump(),
            role=User.Role.ADMIN,
            hashed_password=self.get_password_hash(
                obj_data.password.get_secret_value()
            ),
        )
        return await self.repo.create(session, user_data)

    async def update_user(
            self, session: AsyncSession, obj_data: UserUpdate, user_id: UUID
    ) -> User:
        """Update an existing user."""
        user_data = UserDbUpdate(**obj_data.model_dump())
        if obj_data.password:
            user_data.hashed_password = self.get_password_hash(obj_data.password)
        return await self.repo.update_by_pk(session, pk=user_id, obj_in=user_data)

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        """Get a user by email."""
        return await self.repo.get_by_email(session, email=email)

    async def authenticate(
            self, session: AsyncSession, email: str, password: str
    ) -> User | None:
        user = await self.repo.get_by_email(session, email=email)
        if user is not None and self.is_valid_password(password, user.hashed_password):
            return user
        return None

    def create_access_token(self, user: User) -> str:
        expire = datetime.now(tz=timezone.utc) + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return jwt.encode(
            {"exp": expire, "user_id": str(user.id)},
            key=self.settings.SECRET_KEY.get_secret_value(),
            algorithm=self.ALGORITHM,
        )

    def is_valid_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.context.hash(password)
