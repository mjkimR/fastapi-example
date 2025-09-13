from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.session import get_session
from app.core.exceptions.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
    PermissionDeniedException,
)
from app.models.users import User
from app.services.users import UserService
from app.schemas.token import TokenPayload

oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


def get_token_data(
        token: str = Depends(oauth2),
        user_service: UserService = Depends(),
) -> TokenPayload:
    try:
        secret_key = user_service.settings.SECRET_KEY.get_secret_value()
        payload = jwt.decode(token, secret_key, algorithms=[user_service.ALGORITHM])
        token_data = TokenPayload(**payload)
    except Exception:
        raise InvalidCredentialsException()
    return token_data


async def get_current_user(
        token: TokenPayload = Depends(get_token_data),
        session: AsyncSession = Depends(get_session),
        user_service: UserService = Depends(),
):
    user = await user_service.get(session, obj_id=token.user_id)
    if user is None:
        raise UserNotFoundException()
    return user


def get_current_superuser(user: User = Depends(get_current_user)) -> User:
    if user.role != User.Role.ADMIN:
        raise PermissionDeniedException()
    return user


on_superuser = get_current_superuser
