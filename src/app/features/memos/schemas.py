import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.features.memos.enum import MemoEventType
from app.features.tags.schemas import TagRead
from app_base.base.schemas.mixin import TimestampSchemaMixin, UUIDSchemaMixin


class MemoCreate(BaseModel):
    category: str = Field(description="The category to which the memo belongs, fixed once set.")
    title: str = Field(description="The title of the memo.")
    contents: str = Field(description="The contents of the memo.")
    tags: list[str] = Field(default_factory=list, description="A list of tags for the memo.")


class MemoUpdate(BaseModel):
    title: str | None = Field(default=None, description="The title of the memo.")
    contents: str | None = Field(default=None, description="The contents of the memo.")
    tags: list[str] | None = Field(default=None, description="A list of tags for the memo.")


class MemoRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    category: str = Field(description="The category to which the memo belongs, fixed once set.")
    title: str = Field(description="The title of the memo.")
    contents: str = Field(description="The contents of the memo.")
    workspace_id: uuid.UUID = Field(description="The workspace id of the memo.")
    tags: list[TagRead] = Field(default_factory=list, description="A list of tags for the memo.")

    model_config = ConfigDict(from_attributes=True)


class MemoNotificationPayload(BaseModel):
    """
    Payload schema for memo-related notification events.
    """

    id: uuid.UUID = Field(description="The ID of the memo.")
    workspace_id: uuid.UUID = Field(description="The workspace ID of the memo.")
    user_id: uuid.UUID = Field(description="The user ID who created the memo.")
    title: str = Field(description="The title of the memo.")
    event_type: MemoEventType = Field(description="The event type of the memo notification.")
