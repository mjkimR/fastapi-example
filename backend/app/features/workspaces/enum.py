from enum import Enum


WORKSPACE_RES_NAME = "workspace"


class WorkspaceEventType(Enum, str):
    CREATE = "WORKSPACE_CREATED"
    UPDATE = "WORKSPACE_UPDATED"
    DELETE = "WORKSPACE_DELETED"
