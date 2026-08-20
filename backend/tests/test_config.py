from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings


def test_defaults_are_safe_for_local_development() -> None:
    settings = Settings()

    assert settings.environment is Environment.LOCAL
    assert settings.debug is False
    assert settings.docs_url == "/docs"


def test_debug_is_rejected_in_production() -> None:
    with pytest.raises(ValidationError):
        Settings(environment=Environment.PRODUCTION, debug=True)


def test_docs_are_disabled_in_production() -> None:
    settings = Settings(environment=Environment.PRODUCTION)

    assert settings.docs_url is None
    assert settings.redoc_url is None
    assert settings.openapi_url is None


def test_cors_origins_parsed_from_comma_separated_string() -> None:
    settings = Settings(cors_origins="http://a.example, http://b.example")

    assert settings.cors_origin_list == ["http://a.example", "http://b.example"]


def test_empty_cors_origins_yields_empty_list() -> None:
    settings = Settings(cors_origins="")

    assert settings.cors_origin_list == []


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(log_level="NOT_A_LEVEL")


def test_log_level_is_normalised_to_upper_case() -> None:
    settings = Settings(log_level="debug")

    assert settings.log_level == "DEBUG"


def test_settings_are_immutable() -> None:
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.debug = True  # type: ignore[misc]
