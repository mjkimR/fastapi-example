from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UUIDSchemaMixin, TimestampSchemaMixin
from app.schemas.tags import TagRead


class MemoCreate(BaseModel):
    category: str = Field(..., description="The category to which the memo belongs, fixed once set.")
    title: str = Field(..., description="The title of the memo.")
    contents: str = Field(..., description="The contents of the memo.")
    tags: list[str] = Field([], description="A list of tags for the memo.")


class MemoUpdate(BaseModel):
    title: str | None = Field(default=None, description="The title of the memo.")
    contents: str | None = Field(default=None, description="The contents of the memo.")
    tags: list[str] | None = Field(None, description="A list of tags for the memo.")


class MemoRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    category: str = Field(..., description="The category to which the memo belongs, fixed once set.")
    title: str = Field(..., description="The title of the memo.")
    contents: str = Field(..., description="The contents of the memo.")
    tags: list[TagRead] = Field([], description="A list of tags for the memo.")

    model_config = ConfigDict(from_attributes=True)
