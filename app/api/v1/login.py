from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.session import get_session

from app.schemas.token import Token
from app.services.user import UserService

router = APIRouter(tags=["Login"])


@router.post("/login/", response_model=Token)
async def login(
        data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session),
        service: UserService = Depends(),
):
    user = await service.authenticate(session, email=data.username, password=data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return Token(
        access_token=service.create_access_token(user),
        token_type="bearer",
    )
