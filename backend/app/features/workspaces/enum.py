from enum import Enum


WORKSPACE_RES_NAME = "workspace"


class WorkspaceEventType(str, Enum):
    CREATE = "WORKSPACE_CREATED"
    UPDATE = "WORKSPACE_UPDATED"
    DELETE = "WORKSPACE_DELETED"
