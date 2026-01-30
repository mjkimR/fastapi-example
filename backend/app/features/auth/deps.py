from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.deps import get_session
from app.features.auth.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
    PermissionDeniedException,
)
from app.features.auth.models import User
from app.features.auth.services import UserService
from app.features.auth.token_schemas import TokenPayload

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def get_token_data(
    token: Annotated[str, Depends(oauth2)],
    user_service: Annotated[UserService, Depends()],
) -> TokenPayload:
    try:
        secret_key = user_service.settings.SECRET_KEY.get_secret_value()
        payload = jwt.decode(token, secret_key, algorithms=[user_service.ALGORITHM])
        token_data = TokenPayload(**payload)
    except Exception:
        raise InvalidCredentialsException()
    return token_data


async def get_current_user(
    token: Annotated[TokenPayload, Depends(get_token_data)],
    session: Annotated[AsyncSession, Depends(get_session)],
    user_service: Annotated[UserService, Depends()],
) -> User:
    user = await user_service.get(session, obj_id=token.user_id)
    if user is None:
        raise UserNotFoundException()
    return user


def get_current_superuser(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != User.Role.ADMIN:
        raise PermissionDeniedException()
    return user


on_superuser = get_current_superuser
