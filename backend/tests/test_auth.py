from __future__ import annotations

import uuid
from typing import cast

from fastapi.testclient import TestClient
from httpx import Response


def _unique_email() -> str:
    # The real docker-compose/CI Postgres persists rows across test runs (no
    # per-test transaction rollback), so a fixed literal email would collide with
    # a previous run's data and turn a fresh registration into an unrelated 409.
    return f"{uuid.uuid4()}@example.com"


def _register(
    client: TestClient, email: str, password: str = "correct-horse-1"
) -> Response:
    return cast(
        Response,
        client.post(
            "/api/v1/auth/register", json={"email": email, "password": password}
        ),
    )


def _login(
    client: TestClient, email: str, password: str = "correct-horse-1"
) -> Response:
    return cast(
        Response,
        client.post(
            "/api/v1/auth/login", data={"username": email, "password": password}
        ),
    )


def test_register_creates_a_user(client: TestClient) -> None:
    email = _unique_email()

    response = _register(client, email)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_rejects_a_duplicate_email(client: TestClient) -> None:
    email = _unique_email()
    _register(client, email)

    response = _register(client, email)

    assert response.status_code == 409


def test_register_rejects_a_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register", json={"email": _unique_email(), "password": "short"}
    )

    assert response.status_code == 422


def test_login_returns_a_token_pair(client: TestClient) -> None:
    email = _unique_email()
    _register(client, email)

    response = _login(client, email)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


def test_login_rejects_the_wrong_password(client: TestClient) -> None:
    email = _unique_email()
    _register(client, email)

    response = _login(client, email, password="wrong-password")

    assert response.status_code == 401


def test_login_rejects_an_unknown_email(client: TestClient) -> None:
    response = _login(client, _unique_email())

    assert response.status_code == 401


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_rejects_a_malformed_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


def test_me_returns_the_current_user(client: TestClient) -> None:
    email = _unique_email()
    _register(client, email)
    tokens = _login(client, email).json()

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == email


def test_refresh_returns_a_new_token_pair(client: TestClient) -> None:
    email = _unique_email()
    _register(client, email)
    tokens = _login(client, email).json()

    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_refresh_rejects_an_access_token_used_as_a_refresh_token(
    client: TestClient,
) -> None:
    email = _unique_email()
    _register(client, email)
    tokens = _login(client, email).json()

    response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]}
    )

    assert response.status_code == 401
