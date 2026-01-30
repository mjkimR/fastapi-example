import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Body, status

from app.base.deps.params.page import PaginationParam
from app.base.exceptions.basic import NotFoundException
from app.base.schemas.delete_resp import DeleteResponse
from app.base.schemas.paginated import PaginatedList
from app.features.auth.deps import get_current_user
from app.features.auth.models import User
from app.features.workspaces.schemas import (
    WorkspaceRead,
    WorkspaceUpdate,
    WorkspaceCreate,
)
from app.features.workspaces.usecases.crud import (
    CreateWorkspaceUseCase,
    GetMultiWorkspaceUseCase,
    GetWorkspaceUseCase,
    UpdateWorkspaceUseCase,
    DeleteWorkspaceUseCase,
)

router = APIRouter(
    prefix="/workspaces", tags=["Workspaces"], dependencies=[Depends(get_current_user)]
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=WorkspaceRead)
async def create_workspace(
    use_case: Annotated[CreateWorkspaceUseCase, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    workspace_in: WorkspaceCreate = Body(),
):
    return await use_case.execute(workspace_in, context={"user_id": current_user.id})


@router.get("", response_model=PaginatedList[WorkspaceRead])
async def get_workspaces(
    use_case: Annotated[GetMultiWorkspaceUseCase, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    pagination: PaginationParam,
):
    return await use_case.execute(**pagination, context={"user_id": current_user.id})


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    use_case: Annotated[GetWorkspaceUseCase, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    workspace_id: uuid.UUID,
):
    workspace = await use_case.execute(
        workspace_id, context={"user_id": current_user.id}
    )
    if not workspace:
        raise NotFoundException()
    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    use_case: Annotated[UpdateWorkspaceUseCase, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    workspace_id: uuid.UUID,
    workspace_in: WorkspaceUpdate,
):
    workspace = await use_case.execute(
        workspace_id, workspace_in, context={"user_id": current_user.id}
    )
    if not workspace:
        raise NotFoundException()
    return workspace


@router.delete("/{workspace_id}", response_model=DeleteResponse)
async def delete_workspace(
    use_case: Annotated[DeleteWorkspaceUseCase, Depends()],
    current_user: Annotated[User, Depends(get_current_user)],
    workspace_id: uuid.UUID,
):
    return await use_case.execute(workspace_id, context={"user_id": current_user.id})
