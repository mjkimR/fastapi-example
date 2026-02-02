import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.features.workspaces.enum import WorkspaceEventType
from app_base.base.schemas.mixin import TimestampSchemaMixin, UUIDSchemaMixin


class WorkspaceCreate(BaseModel):
    name: str = Field(..., description="The name of the workspace.")


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, description="The name of the workspace.")


class WorkspaceRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    name: str = Field(..., description="The name of the workspace.")
    created_by: uuid.UUID = Field(..., description="The user who created the workspace.")
    updated_by: uuid.UUID | None = Field(None, description="The user who last updated the workspace.")

    model_config = ConfigDict(from_attributes=True)


class WorkspaceNotificationPayload(BaseModel):
    """
    Payload schema for workspace-related notification events.
    """

    id: uuid.UUID = Field(description="The ID of the workspace.")
    name: str = Field(description="The name of the workspace.")
    user_id: uuid.UUID = Field(description="The ID of the user performing the action.")
    event_type: WorkspaceEventType = Field(description="The event type of the workspace notification.")
