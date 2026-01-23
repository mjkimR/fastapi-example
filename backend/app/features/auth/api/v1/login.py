from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.session import get_session
from app.core.exceptions.exceptions import IncorrectEmailOrPasswordException
from app.features.auth.token_schemas import Token
from app.features.auth.services import UserService

router = APIRouter(tags=["Login"])


@router.post("/login/", response_model=Token)
async def login(
        data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    user = await service.authenticate(session, email=data.username, password=data.password)
    if user is None:
        raise IncorrectEmailOrPasswordException()
    return Token(
        access_token=service.create_access_token(user),
        token_type="bearer",
    )
