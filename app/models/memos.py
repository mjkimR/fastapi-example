from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from app.models.base import (Base, UUIDMixin, TimestampMixin)


class Memo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memos"

    category: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(200))
    contents: Mapped[str] = mapped_column()
