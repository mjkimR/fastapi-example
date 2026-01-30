import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.base.schemas.mixin import UUIDSchemaMixin, TimestampSchemaMixin
from app.features.memos.enum import MemoEventType
from app.features.memos.models import Memo
from app.features.tags.schemas import TagRead


class MemoCreate(BaseModel):
    category: str = Field(
        description="The category to which the memo belongs, fixed once set."
    )
    title: str = Field(description="The title of the memo.")
    contents: str = Field(description="The contents of the memo.")
    tags: list[str] = Field(
        default_factory=list, description="A list of tags for the memo."
    )


class MemoUpdate(BaseModel):
    title: str | None = Field(default=None, description="The title of the memo.")
    contents: str | None = Field(default=None, description="The contents of the memo.")
    tags: list[str] | None = Field(
        default=None, description="A list of tags for the memo."
    )


class MemoRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    category: str = Field(
        description="The category to which the memo belongs, fixed once set."
    )
    title: str = Field(description="The title of the memo.")
    contents: str = Field(description="The contents of the memo.")
    workspace_id: uuid.UUID = Field(description="The workspace id of the memo.")
    tags: list[TagRead] = Field(
        default_factory=list, description="A list of tags for the memo."
    )

    model_config = ConfigDict(from_attributes=True)


class MemoNotificationPayload(BaseModel):
    """
    Payload schema for memo-related notification events.
    """

    id: uuid.UUID = Field(description="The ID of the memo.")
    workspace_id: uuid.UUID = Field(description="The workspace ID of the memo.")
    user_id: uuid.UUID = Field(description="The user ID who created the memo.")
    title: str = Field(description="The title of the memo.")
    event_type: MemoEventType = Field(
        description="The event type of the memo notification."
    )

    @classmethod
    def from_orm(
        cls,
        orm_obj: "Memo",
        user_id: uuid.UUID,
        event_type: MemoEventType,
    ) -> dict:
        return cls(
            id=orm_obj.id,
            workspace_id=orm_obj.workspace_id,
            user_id=user_id,
            title=orm_obj.title,
            event_type=event_type,
        ).model_dump()
