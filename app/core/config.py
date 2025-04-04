import functools
import os
from pydantic_settings import BaseSettings
import pathlib


def get_env_filename():
    runtime_env = os.getenv("ENV")
    home = pathlib.Path(__file__).parent.parent.parent.resolve()

    return f"{home}/.env.{runtime_env}" if runtime_env else f"{home}/.env"


if os.path.exists(get_env_filename()):
    from dotenv import load_dotenv

    load_dotenv(get_env_filename())


class AppSettings(BaseSettings):
    pass


@functools.lru_cache
def get_app_settings():
    return AppSettings()
