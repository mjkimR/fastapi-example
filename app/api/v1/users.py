import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_superuser, get_current_user, on_superuser
from app.core.deps.session import get_session
from app.models.user import User
from app.schemas.user import UserRead, UsersRead, UserCreate, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead, dependencies=[Depends(on_superuser)])
async def create_user(
        user_in: UserCreate,
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    """Create new user."""
    user = await service.get_by_email(session, email=str(user_in.email))
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this username already exists in the system",
        )
    user = await service.create_user(session, obj_data=user_in)
    return user


@router.get("/", response_model=UsersRead, dependencies=[Depends(on_superuser)])
async def read_users(
        offset: int = Query(0, ge=0),
        limit: int = Query(100, gt=0, le=1000),
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    """Get user list."""
    users = await service.get_multi(session, offset=offset, limit=limit)
    return users


@router.get("/{user_id}", response_model=UsersRead)
async def read_user(
        user_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    """Get a specific user by id."""
    if current_user.id == user_id:
        return current_user
    if current_user.role != User.Role.ADMIN:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    user = await service.get_by_id(session, obj_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead, dependencies=[Depends(on_superuser)])
async def update_user(
        user_id: uuid.UUID,
        user_in: UserUpdate,
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    user = await service.update_by_id(session, obj_id=user_id, obj_data=user_in)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return user


@router.delete("/{user_id}")
async def delete_user(
        user_id: uuid.UUID,
        current_user: User = Depends(get_current_superuser),
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="User can't delete itself")
    if await service.delete_by_id(session, user_id):
        return {"detail": f"User with id {user_id} has been deleted"}
    else:
        raise HTTPException(status_code=404, detail="Not found")
