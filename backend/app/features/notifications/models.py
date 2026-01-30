import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base.models.mixin import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.features.auth.models import User


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    user: Mapped["User"] = relationship()

    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)

    event_type: Mapped[Optional[str]] = mapped_column(
        String(100), default=None, nullable=True, index=True
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        String(100), default=None, nullable=True
    )
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), default=None, nullable=True
    )
