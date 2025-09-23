from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import UUIDSchemaMixin, TimestampSchemaMixin


class TagCreate(BaseModel):
    name: str = Field(..., description="The name of the tag.")


class TagRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    name: str = Field(..., description="The name of the tag.")

    model_config = ConfigDict(from_attributes=True)


class TagsRead(BaseModel):
    data: list[TagRead] = Field(..., description="The list of tags.")
    total_count: int = Field(..., description="The total number of tags.")

    model_config = ConfigDict(from_attributes=True)
