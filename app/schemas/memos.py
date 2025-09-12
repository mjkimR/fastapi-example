from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UUIDSchemaMixin, TimestampSchemaMixin


class MemoCreate(BaseModel):
    category: str = Field(..., description="The category to which the memo belongs, fixed once set.")
    title: str = Field(..., description="The title of the memo.")
    contents: str = Field(..., description="The contents of the memo.")


class MemoUpdate(BaseModel):
    title: str | None = Field(None, description="The title of the memo.")
    contents: str | None = Field(None, description="The contents of the memo.")


class MemoRead(MemoCreate, UUIDSchemaMixin, TimestampSchemaMixin):
    model_config = ConfigDict(from_attributes=True)
