from enum import StrEnum
from sqlalchemy.orm import mapped_column, Mapped

from app.base.models.mixin import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column()
    surname: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()

    class Role(StrEnum):
        ADMIN = "admin"
        USER = "user"
