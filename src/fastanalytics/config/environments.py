from typing import Literal

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

env = Literal["dev", "prod"]


class AppSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=(".app.env",),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    pg_dsn: PostgresDsn
    log_level: str = "INFO"
    timezone: str
    environment: env = "dev"
    app: AppSettings


environ = _Settings()  # pyright: ignore[reportCallIssue]
