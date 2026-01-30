import enum
import datetime
from typing import Any, Optional
from sqlalchemy import String, JSON, Enum as EnumColumn, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.base.models.mixin import Base, UUIDMixin, TimestampMixin


class EventStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Outbox(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "outbox"

    aggregate_type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[EventStatus] = mapped_column(
        EnumColumn(EventStatus), nullable=False, default=EventStatus.PENDING, index=True
    )

    retry_count: Mapped[int] = mapped_column(default=0)
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
