from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

from app.core.config import get_app_settings
from app.models.users import User
from app.repos.users import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserDbCreate, UserDbUpdate
from app.services.base import BaseService

"""
* https://github.com/ViktorViskov/fastapi-mvc/blob/main/app/utils/bcrypt_hashing.py
* https://github.com/ViktorViskov/fastapi-mvc/blob/main/app/utils/sha256_hashing.py
* https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/core/security.py
* https://github.com/Kludex/fastapi-microservices/blob/main/users/app/core/security.py
"""


class UserService(BaseService[UserRepository, User, UserDbCreate, UserDbUpdate]):
    """Service class for handling user-related operations."""
    ALGORITHM = "HS256"

    def __init__(
            self,
            settings=Depends(get_app_settings),
            repo: UserRepository = Depends(UserRepository.get_repo),
    ):
        self.settings = settings
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        super().__init__(repo)

    async def create_user(self, session: AsyncSession, obj_data: UserCreate) -> User:
        """Create a new user."""
        user_data = UserDbCreate(
            **obj_data.model_dump(), role=User.Role.USER,
            hashed_password=self.get_password_hash(obj_data.password.get_secret_value())
        )
        return await self.repo.create(session, user_data)

    async def create_admin(self, session: AsyncSession, obj_data: UserCreate) -> User:
        """Create a new admin user."""
        user_data = UserDbCreate(
            **obj_data.model_dump(), role=User.Role.ADMIN,
            hashed_password=self.get_password_hash(obj_data.password.get_secret_value())
        )
        return await self.repo.create(session, user_data)

    async def create_guest(self, session: AsyncSession, obj_data: UserCreate) -> User:
        """Create a new guest user."""
        user_data = UserDbCreate(
            **obj_data.model_dump(), role=User.Role.GUEST,
            hashed_password=self.get_password_hash(obj_data.password.get_secret_value())
        )
        return await self.repo.create(session, user_data)

    async def update_user(self, session: AsyncSession, obj_data: UserUpdate, user_id: str) -> User:
        """Update an existing user."""
        user_data = UserDbUpdate(**obj_data.model_dump())
        if obj_data.password:
            user_data.hashed_password = self.get_password_hash(obj_data.password)
        return await self.repo.update_by_pk(session, pk=user_id, obj_in=user_data, commit=True)

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
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return jwt.encode(
            {"exp": expire, "user_id": str(user.id)},
            key=self.settings.SECRET_KEY.get_secret_value(),
            algorithm=self.ALGORITHM,
        )

    def is_valid_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.context.hash(password)
