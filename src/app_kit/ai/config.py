import functools

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class VectorDBSettings(BaseSettings):
    KIND: str = Field(default="qdrant")
    URL: str = Field(default="http://localhost:6333")
    API_KEY: SecretStr = Field()

    model_config = SettingsConfigDict(
        env_prefix="VECTOR_DB_",
        env_ignore_empty=True,
        validate_assignment=True,
        extra="ignore",
    )


@functools.lru_cache
def get_vector_db_settings():
    return VectorDBSettings()  # type: ignore
