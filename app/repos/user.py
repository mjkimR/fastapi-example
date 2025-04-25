from app.models.user import User
from app.repos.base import BaseRepository
from app.schemas.user import UserDbCreate, UserDbUpdate


class UserRepository(BaseRepository[User, UserDbCreate, UserDbUpdate]):
    """Repository for User model."""

    @staticmethod
    def get_repo() -> "UserRepository":
        """Get an instance of UserRepository."""
        return UserRepository(
            model=User,
            default_order_by_col="updated_at",
        )

    async def get_by_email(self, session, email: str) -> User | None:
        """Get a user by email."""
        stmt = self._select(where=User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
