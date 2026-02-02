from app_base.base.repos.base import BaseRepository
from app.features.workspaces.models import Workspace


class WorkspaceRepository(BaseRepository):
    model = Workspace
