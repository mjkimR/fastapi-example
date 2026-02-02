from app.features.workspaces.models import Workspace
from app_base.base.repos.base import BaseRepository


class WorkspaceRepository(BaseRepository):
    model = Workspace
