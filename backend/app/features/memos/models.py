from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
import uuid
from typing import TYPE_CHECKING

from app.base.models.mixin import (Base, UUIDMixin, TimestampMixin, AuditMixin)
from app.features.tags.models import memo_tag_association

if TYPE_CHECKING:
    from app.features.workspaces.models import Workspace


class Memo(Base, UUIDMixin, TimestampMixin, AuditMixin):
    __tablename__ = "memos"

    category: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(200))
    contents: Mapped[str] = mapped_column()

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="memos")

    tags = relationship("Tag", secondary=memo_tag_association, back_populates="memos", lazy="selectin")
