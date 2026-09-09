import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


def _get_env_path() -> str:
    env_path = os.path.join(BASE_DIR, "envs", ".env")
    return env_path


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    ADMIN_JWT_SECRET: str
    PARTICIPANT_JWT_SECRET: str
    JWT_ALG: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    TEST_ADMIN_JWT_SECRET: str
    TEST_PARTICIPANT_JWT_SECRET: str
    TEST_JWT_ALG: str

    DOCS_URL_ENABLED: Optional[str] = None
    REDOC_URL_ENABLED: Optional[str] = None
    OPENAPI_URL_ENABLED: Optional[str] = None

    ALLOW_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"

    model_config = SettingsConfigDict(env_file=_get_env_path())


settings = Settings()  # type: ignore
