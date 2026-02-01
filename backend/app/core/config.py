import functools
import os
import pathlib

from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings


def get_repo_path():
    """Get the path to the repository."""
    path = str(pathlib.Path(__file__).parent.parent.parent.parent.resolve())
    return path


def get_env_filename():
    runtime_env = os.getenv("ENV")
    home = get_repo_path()

    return f"{home}/.env.{runtime_env}" if runtime_env else f"{home}/.env"


if os.path.exists(get_env_filename()):
    from dotenv import load_dotenv

    load_dotenv(get_env_filename())


class AppSettings(BaseSettings):
    DATABASE_URL: str = Field(default=f"sqlite+aiosqlite:///{get_repo_path()}/.test.db")

    FIRST_USER_EMAIL: EmailStr
    FIRST_USER_PASSWORD: SecretStr

    SECRET_KEY: SecretStr  # openssl rand -hex 64
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10)

    LOG_JSON_FORMAT: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")


@functools.lru_cache
def get_app_settings():
    return AppSettings()  # type: ignore
