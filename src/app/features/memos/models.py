import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.features.tags.models import memo_tag_association
from app_base.base.models.mixin import AuditMixin, Base, TimestampMixin, UUIDMixin

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
