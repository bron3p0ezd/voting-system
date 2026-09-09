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

    JWT_SECRET_KEY_VAL: str
    JWT_ALG_VAL: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    TEST_JWT_SECRET_KEY_VAL: str
    TEST_JWT_ALG_VAL: str

    DOCS_URL_ENABLED: Optional[str] = None
    REDOC_URL_ENABLED: Optional[str] = None
    OPENAPI_URL_ENABLED: Optional[str] = None

    ALLOW_ORIGINS: list[str] = [
        "",
    ]

    @property
    def JWT_SECRET_KEY(self) -> str:
        return self.JWT_SECRET_KEY_VAL

    @property
    def JWT_ALG(self) -> str:
        return self.JWT_ALG_VAL

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TEST_JWT_SECRET_KEY(self) -> str:
        return self.TEST_JWT_SECRET_KEY_VAL

    @property
    def TEST_JWT_ALG(self) -> str:
        return self.TEST_JWT_ALG_VAL

    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"

    model_config = SettingsConfigDict(env_file=_get_env_path())


settings = Settings()  # type: ignore
