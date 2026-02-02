from enum import StrEnum

from sqlalchemy.orm import Mapped, mapped_column

from app_base.base.models.mixin import Base, TimestampMixin, UUIDMixin


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
