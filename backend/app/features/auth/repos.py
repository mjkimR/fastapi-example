from app.features.auth.models import User
from app.base.repos.base import BaseRepository
from app.features.auth.schemas import UserDbCreate, UserDbUpdate


class UserRepository(BaseRepository[User, UserDbCreate, UserDbUpdate]):
    """Repository for User model."""

    model = User

    async def get_by_email(self, session, email: str) -> User | None:
        """Get a user by email."""
        stmt = self._select(where=User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
