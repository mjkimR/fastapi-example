import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

from app.base.schemas.mixin import UUIDSchemaMixin, TimestampSchemaMixin
from app.features.outbox.models import EventStatus


class OutboxCreate(BaseModel):
    aggregate_type: str = Field(
        ..., description="The type of the aggregate root. e.g., 'memo'"
    )
    aggregate_id: str = Field(
        ..., description="The ID of the aggregate root. e.g., memo.id"
    )
    event_type: str = Field(
        ..., description="The type of the event. e.g., 'MEMO_CREATED'"
    )
    payload: dict[str, Any] = Field(..., description="The event payload.")


class OutboxUpdate(BaseModel):
    status: EventStatus | None = None
    retry_count: int | None = None
    processed_at: datetime.datetime | None = None


class OutboxRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: dict[str, Any]
    status: EventStatus
    retry_count: int
    processed_at: datetime.datetime | None = None

    model_config = ConfigDict(from_attributes=True)
