from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_app_settings
from app.crud.users import crud_user
from app.models.users import User


class SecurityService:
    """Service class for handling security-related operations."""

    ALGORITHM = "HS256"

    def __init__(
            self,
            settings=Depends(get_app_settings)
    ):
        self.settings = settings
        self.context = CryptContext(schemes=["bcrypt"], deprecated="auto")



