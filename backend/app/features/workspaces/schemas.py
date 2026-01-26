from pydantic import BaseModel, ConfigDict, Field
import uuid
from app.base.schemas.mixin import UUIDSchemaMixin, TimestampSchemaMixin


class WorkspaceCreate(BaseModel):
    name: str = Field(..., description="The name of the workspace.")


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, description="The name of the workspace.")


class WorkspaceRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    name: str = Field(..., description="The name of the workspace.")
    created_by: uuid.UUID = Field(..., description="The user who created the workspace.")
    updated_by: uuid.UUID | None = Field(None, description="The user who last updated the workspace.")

    model_config = ConfigDict(from_attributes=True)
