from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_base.base.models.mixin import AuditMixin, Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.features.memos.models import Memo
    from app.features.tags.models import Tag


class Workspace(Base, UUIDMixin, TimestampMixin, AuditMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    memos: Mapped[List["Memo"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
