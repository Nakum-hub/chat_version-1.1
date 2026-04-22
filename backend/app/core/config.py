from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="CYBERFYX_",
        extra="ignore",
        case_sensitive=False,
        env_ignore_empty=True,
    )

    environment: str = "development"
    debug: bool = False
    app_name: str = "Cyberfyx Backend"
    database_url: str = "sqlite:///./cyberfyx.db"
    cors_origins: str = "http://127.0.0.1:4321,http://localhost:4321,http://127.0.0.1:8080,http://localhost:8080"
    enable_internal_api: bool = False

    jwt_secret_key: str = "replace-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    inquiry_rate_limit_window_minutes: int = 15
    inquiry_rate_limit_count: int = 5
    inquiry_duplicate_window_hours: int = 24

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_from_email: str | None = None
    smtp_sales_to: str = "sales@cyberfyx.net"

    @model_validator(mode="after")
    def _validate_production_settings(self) -> "Settings":
        if self.environment.lower() == "production" and self.jwt_secret_key == "replace-me":
            raise ValueError("JWT_SECRET_KEY must be overridden in production.")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        value: Any = self.cors_origins
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raise ValueError("CORS_ORIGINS must be a comma-separated string or list of origins.")

    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_from_email and self.smtp_sales_to)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
