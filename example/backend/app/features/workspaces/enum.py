from enum import Enum


class WorkspaceEventType(str, Enum):
    CREATE = "WORKSPACE_CREATED"
    UPDATE = "WORKSPACE_UPDATED"
    DELETE = "WORKSPACE_DELETED"
