
from sqlalchemy import Column, String, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.base.models.mixin import Base, UUIDMixin, TimestampMixin
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.workspaces.models import Workspace

memo_tag_association = Table(
    "memo_tag_association",
    Base.metadata,
    Column("memo_id", ForeignKey("memos.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint('name', 'workspace_id', name='_name_workspace_uc'),
    )

    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    workspace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="tags")

    memos = relationship("Memo", secondary=memo_tag_association, back_populates="tags")
