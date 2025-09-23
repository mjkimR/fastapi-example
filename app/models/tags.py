
from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, UUIDMixin, TimestampMixin

memo_tag_association = Table(
    "memo_tag_association",
    Base.metadata,
    Column("memo_id", ForeignKey("memos.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    memos = relationship("Memo", secondary=memo_tag_association, back_populates="tags")
