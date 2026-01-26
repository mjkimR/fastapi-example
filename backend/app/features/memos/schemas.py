import uuid
from pydantic import BaseModel, ConfigDict, Field

from app.base.schemas.mixin import UUIDSchemaMixin, TimestampSchemaMixin
from app.features.tags.schemas import TagRead


class MemoCreate(BaseModel):
    category: str = Field(..., description="The category to which the memo belongs, fixed once set.")
    title: str = Field(..., description="The title of the memo.")
    contents: str = Field(..., description="The contents of the memo.")
    tags: list[str] = Field([], description="A list of tags for the memo.")


class MemoUpdate(BaseModel):
    title: str | None = Field(default=None, description="The title of the memo.")
    contents: str | None = Field(default=None, description="The contents of the memo.")
    tags: list[str] | None = Field(default=None, description="A list of tags for the memo.")


class MemoRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    category: str = Field(..., description="The category to which the memo belongs, fixed once set.")
    title: str = Field(..., description="The title of the memo.")
    contents: str = Field(..., description="The contents of the memo.")
    workspace_id: uuid.UUID = Field(..., description="The workspace id of the memo.")
    tags: list[TagRead] = Field([], description="A list of tags for the memo.")

    model_config = ConfigDict(from_attributes=True)
