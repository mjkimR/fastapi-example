from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from app_base.base.schemas.mixin import TimestampSchemaMixin, UUIDSchemaMixin
from app.features.auth.models import User


class UserCreate(BaseModel):
    name: str = Field(..., description="The user's first name.")
    surname: str = Field(..., description="The user's last name.")
    email: EmailStr = Field(..., description="The user's email address.")
    password: SecretStr = Field(..., description="The user's password.")


class UserDbCreate(BaseModel):
    name: str = Field(..., description="The user's first name.")
    surname: str = Field(..., description="The user's last name.")
    email: EmailStr = Field(..., description="The user's email address.")
    hashed_password: str = Field(..., description="The user's hashed password.")
    role: User.Role = Field(..., description="The user's role.")


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, description="The user's first name.")
    surname: str | None = Field(default=None, description="The user's last name.")
    password: SecretStr | None = Field(default=None, description="The user's password.")


class UserDbUpdate(BaseModel):
    name: str | None = Field(default=None, description="The user's first name.")
    surname: str | None = Field(default=None, description="The user's last name.")
    password: SecretStr | None = Field(default=None, description="The user's password.")
    hashed_password: str | None = Field(default=None, description="The user's hashed password.")


class UserRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    name: str = Field(..., description="The user's first name.")
    surname: str = Field(..., description="The user's last name.")
    role: User.Role = Field(..., description="The user's role.")
    email: EmailStr = Field(..., description="The user's email address.")

    model_config = ConfigDict(from_attributes=True)


class UsersRead(BaseModel):
    data: list[UserRead] = Field(..., description="The list of users.")
    total_count: int = Field(..., description="The total number of users.")

    model_config = ConfigDict(from_attributes=True)
