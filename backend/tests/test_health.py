from __future__ import annotations

from fastapi.testclient import TestClient


def test_livez_returns_200_and_does_not_report_readiness(client: TestClient) -> None:
    response = client.get("/livez")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_readyz_returns_200(client: TestClient) -> None:
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_health_endpoints_are_unversioned(client: TestClient) -> None:
    assert client.get("/api/v1/livez").status_code == 404
    assert client.get("/api/v1/readyz").status_code == 404
