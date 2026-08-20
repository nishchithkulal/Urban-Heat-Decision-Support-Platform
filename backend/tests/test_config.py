from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings


def _settings(**overrides: Any) -> Settings:
    # Settings.model_config points at ".env" for real local-development runs (see
    # app/main.py / README). Without disabling that here, these tests would read
    # whatever a developer's own .env happens to contain and stop being deterministic
    # — the opposite of what CLAUDE.md section 17 asks for.
    return Settings(_env_file=None, **overrides)


def test_defaults_are_safe_for_local_development() -> None:
    settings = _settings()

    assert settings.environment is Environment.LOCAL
    assert settings.debug is False
    assert settings.docs_url == "/docs"


def test_debug_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError):
        _settings(environment=Environment.PRODUCTION, debug=True)


def test_docs_are_disabled_in_production() -> None:
    settings = _settings(environment=Environment.PRODUCTION)

    assert settings.docs_url is None
    assert settings.redoc_url is None
    assert settings.openapi_url is None


def test_cors_origins_parsed_from_comma_separated_string() -> None:
    settings = _settings(cors_origins="http://a.example, http://b.example")

    assert settings.cors_origin_list == ["http://a.example", "http://b.example"]


def test_empty_cors_origins_yields_empty_list() -> None:
    settings = _settings(cors_origins="")

    assert settings.cors_origin_list == []


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(log_level="NOT_A_LEVEL")


def test_log_level_is_normalised_to_upper_case() -> None:
    settings = _settings(log_level="debug")

    assert settings.log_level == "DEBUG"


def test_settings_are_immutable() -> None:
    settings = _settings()

    with pytest.raises(ValidationError):
        settings.debug = True  # type: ignore[misc]


def test_default_database_url_uses_asyncpg_driver() -> None:
    settings = _settings()

    assert settings.database_url.startswith("postgresql+asyncpg://")


def test_non_asyncpg_database_url_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _settings(database_url="postgresql://user:pass@localhost/heatpilot")
