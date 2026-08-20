from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import get_db


def test_livez_returns_200_and_does_not_report_readiness(client: TestClient) -> None:
    response = client.get("/livez")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readyz_returns_200_when_database_is_reachable(client: TestClient) -> None:
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readyz_returns_503_when_database_is_unreachable(app: FastAPI) -> None:
    class _BrokenSession:
        async def execute(self, *args: object, **kwargs: object) -> None:
            raise SQLAlchemyError("simulated outage")

    async def _broken_db() -> AsyncIterator[_BrokenSession]:
        yield _BrokenSession()

    app.dependency_overrides[get_db] = _broken_db
    try:
        with TestClient(app) as test_client:
            response = test_client.get("/readyz")
    finally:
        del app.dependency_overrides[get_db]

    assert response.status_code == 503
    assert response.json()["detail"] == "Database unavailable"


def test_health_endpoints_are_unversioned(client: TestClient) -> None:
    assert client.get("/api/v1/livez").status_code == 404
    assert client.get("/api/v1/readyz").status_code == 404
