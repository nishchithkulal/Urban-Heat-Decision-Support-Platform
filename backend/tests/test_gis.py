from __future__ import annotations

import random
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.modules.auth.models import Role, User

pytestmark = pytest.mark.anyio


def _random_point() -> tuple[float, float]:
    return random.uniform(-80.0, 80.0), random.uniform(-170.0, 170.0)


@pytest.fixture
async def admin_headers(settings: Settings, client: TestClient) -> dict[str, str]:
    # There is no API for granting the admin role (deliberately -- self-service
    # privilege escalation would defeat the point of RBAC), so tests promote a
    # freshly registered user directly through the ORM, the same way an operator
    # would via a one-off script or DB console.
    #
    # A fresh engine (not app.state.db_engine) matters here: the TestClient drives
    # the ASGI app through its own internal event loop, separate from the one
    # pytest-anyio runs this async fixture in. asyncpg connections are bound to the
    # loop that opened them, so reusing app.state's engine/pool from this loop would
    # hand a request handler a connection opened on a different loop and crash.
    email = f"{uuid.uuid4()}@example.com"
    password = "correct-horse-1"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})

    engine = create_engine(settings)
    try:
        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one()
            user.role = Role.ADMIN
            await session.commit()
    finally:
        await engine.dispose()

    login = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_location_requires_authentication(client: TestClient) -> None:
    latitude, longitude = _random_point()

    response = client.post(
        "/api/v1/gis/locations",
        json={"name": "test", "latitude": latitude, "longitude": longitude},
    )

    assert response.status_code == 401


def test_create_location_requires_admin_role(client: TestClient) -> None:
    email = f"{uuid.uuid4()}@example.com"
    password = "correct-horse-1"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post(
        "/api/v1/auth/login", data={"username": email, "password": password}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    latitude, longitude = _random_point()

    response = client.post(
        "/api/v1/gis/locations",
        json={"name": "test", "latitude": latitude, "longitude": longitude},
        headers=headers,
    )

    assert response.status_code == 403


async def test_admin_can_create_and_retrieve_a_location(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    latitude, longitude = _random_point()
    name = f"test-location-{uuid.uuid4()}"

    create_response = client.post(
        "/api/v1/gis/locations",
        json={"name": name, "latitude": latitude, "longitude": longitude},
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["name"] == name
    assert body["latitude"] == pytest.approx(latitude, abs=1e-6)
    assert body["longitude"] == pytest.approx(longitude, abs=1e-6)

    get_response = client.get(f"/api/v1/gis/locations/{body['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == name


def test_get_location_returns_404_for_an_unknown_id(client: TestClient) -> None:
    response = client.get(f"/api/v1/gis/locations/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_nearby_locations_finds_a_created_location(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    latitude, longitude = _random_point()
    name = f"test-location-{uuid.uuid4()}"
    client.post(
        "/api/v1/gis/locations",
        json={"name": name, "latitude": latitude, "longitude": longitude},
        headers=admin_headers,
    )

    response = client.get(
        "/api/v1/gis/locations/nearby",
        params={"latitude": latitude, "longitude": longitude, "radius_km": 1.0},
    )

    assert response.status_code == 200
    names = [entry["name"] for entry in response.json()]
    assert name in names


def test_nearby_locations_rejects_an_invalid_radius(client: TestClient) -> None:
    response = client.get(
        "/api/v1/gis/locations/nearby",
        params={"latitude": 0, "longitude": 0, "radius_km": -5},
    )

    assert response.status_code == 422
