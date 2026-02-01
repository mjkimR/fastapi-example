import uuid

from pydantic import BaseModel, ConfigDict, Field

from app_kit.base.schemas.mixin import TimestampSchemaMixin, UUIDSchemaMixin


class NotificationCreate(BaseModel):
    user_id: uuid.UUID = Field(..., description="The ID of the user to notify.")
    message: str = Field(..., description="The notification message.")
    event_type: str | None = Field(
        default=None,
        description="Optional type of the event triggering the notification.",
    )
    resource_type: str | None = Field(default=None, description="Optional type of the related resource.")
    resource_id: uuid.UUID | None = Field(default=None, description="Optional ID of the related resource.")


class NotificationUpdate(BaseModel):
    is_read: bool | None = Field(None, description="Whether the notification has been read.")


class NotificationRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    user_id: uuid.UUID = Field(..., description="The ID of the user to notify.")
    message: str = Field(..., description="The notification message.")
    is_read: bool = Field(..., description="Whether the notification has been read.")

    event_type: str | None = Field(
        default=None,
        description="Optional type of the event triggering the notification.",
    )
    resource_type: str | None = Field(default=None, description="Optional type of the related resource.")
    resource_id: uuid.UUID | None = Field(default=None, description="Optional ID of the related resource.")

    model_config = ConfigDict(from_attributes=True)
