from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    # _env_file=None: tests must not silently pick up whatever a developer's own
    # .env happens to contain (see tests/test_config.py for the failure mode this
    # avoids). database_url is left to its default, which matches docker-compose.yml.
    return Settings(
        _env_file=None, cors_origins="http://localhost:3000", log_json=False
    )


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings=settings)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def anyio_backend() -> str:
    # Tests that talk to the async engine directly (not through TestClient, which
    # drives the ASGI app itself) need an event loop. asyncpg only supports asyncio,
    # so there is no trio backend to parametrize against here.
    return "asyncio"
