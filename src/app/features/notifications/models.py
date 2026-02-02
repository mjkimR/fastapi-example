import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_base.base.models.mixin import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.features.auth.models import User


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship()

    message: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)

    event_type: Mapped[Optional[str]] = mapped_column(String(100), default=None, nullable=True, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), default=None, nullable=True)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), default=None, nullable=True)
