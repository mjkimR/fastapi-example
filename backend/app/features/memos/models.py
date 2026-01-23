from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.base.models.mixin import (Base, UUIDMixin, TimestampMixin)
from app.features.tags.models import memo_tag_association


class Memo(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memos"

    category: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(200))
    contents: Mapped[str] = mapped_column()

    tags = relationship("Tag", secondary=memo_tag_association, back_populates="memos", lazy="selectin")
