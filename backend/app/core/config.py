"""Application configuration.

All configuration enters the application here and nowhere else. Modules receive a
``Settings`` instance by dependency injection rather than reading the environment
directly. That keeps configuration testable, and it means extracting a module into its
own service later is a matter of moving code rather than hunting down scattered
``os.getenv`` calls (CLAUDE.md section 12).
"""

from __future__ import annotations

import logging
from enum import StrEnum
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_VALID_LOG_LEVELS = frozenset(logging.getLevelNamesMapping())


class Environment(StrEnum):
    """Deployment environment.

    Drives safety defaults (for example, whether interactive API docs are exposed)
    rather than being merely informational.
    """

    LOCAL = "local"
    CI = "ci"
    STAGING = "staging"
    PRODUCTION = "production"

    @property
    def is_production(self) -> bool:
        return self is Environment.PRODUCTION


class Settings(BaseSettings):
    """Typed, validated application settings.

    Frozen so configuration cannot drift at runtime: a setting that can be mutated
    after startup is a setting that will eventually be mutated by accident.
    """

    model_config = SettingsConfigDict(
        env_prefix="HEATPILOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    project_name: str = "HeatPilot AI"
    version: str = "0.1.0"
    environment: Environment = Environment.LOCAL
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    log_level: str = "INFO"
    log_json: bool = True

    # Comma-separated, e.g. "http://localhost:3000,https://app.example.com".
    #
    # Deliberately a plain string rather than list[str]: pydantic-settings decodes
    # complex-typed fields as JSON, so a list field would force operators to write
    # '["http://localhost:3000"]' into .env files and Kubernetes ConfigMaps. Environment
    # variables are strings; treating them as such avoids a well-known deployment
    # footgun.
    cors_origins: str = ""

    @field_validator("log_level")
    @classmethod
    def _normalise_log_level(cls, value: str) -> str:
        level = value.strip().upper()
        if level not in _VALID_LOG_LEVELS:
            raise ValueError(
                f"invalid log level {value!r}; "
                f"expected one of {sorted(_VALID_LOG_LEVELS)}"
            )
        return level

    @model_validator(mode="after")
    def _forbid_debug_in_production(self) -> Settings:
        """Fail fast rather than leaking internals.

        ``debug`` widens error output, so allowing it in production would undermine
        the error-handling guarantees in section 19. Refusing to start is safer than
        starting insecurely.
        """
        if self.debug and self.environment.is_production:
            raise ValueError("debug must be disabled when environment is 'production'")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        origins = self.cors_origins.split(",")
        return [origin.strip() for origin in origins if origin.strip()]

    @property
    def docs_url(self) -> str | None:
        """Interactive docs stay available everywhere except production."""
        return None if self.environment.is_production else "/docs"

    @property
    def redoc_url(self) -> str | None:
        return None if self.environment.is_production else "/redoc"

    @property
    def openapi_url(self) -> str | None:
        return None if self.environment.is_production else "/openapi.json"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings once per process.

    Intended for the composition root (application startup) only. Request handlers
    should depend on ``app.api.deps.get_settings_dependency`` so that tests can supply
    their own settings without touching global state.
    """
    return Settings()
