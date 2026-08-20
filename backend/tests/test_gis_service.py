from __future__ import annotations

import random
import uuid
from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.modules.gis import service

pytestmark = pytest.mark.anyio


def _random_point() -> tuple[float, float]:
    # A fresh random point per test run avoids collisions with rows a previous test
    # run left behind in the persistent docker-compose/CI database (see test_auth.py
    # for the same rationale with emails).
    return random.uniform(-80.0, 80.0), random.uniform(-170.0, 170.0)


@pytest.fixture
async def session(settings: Settings) -> AsyncIterator[AsyncSession]:
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    async with session_factory() as db_session:
        yield db_session
    await engine.dispose()


async def test_create_and_get_location_round_trips_coordinates(
    session: AsyncSession,
) -> None:
    latitude, longitude = _random_point()
    name = f"test-location-{uuid.uuid4()}"

    created = await service.create_location(
        session,
        name=name,
        description="a test location",
        latitude=latitude,
        longitude=longitude,
    )
    fetched = await service.get_location(session, created.id)

    assert fetched is not None
    got_lat, got_lon = service.coordinates_of(fetched)
    assert got_lat == pytest.approx(latitude, abs=1e-6)
    assert got_lon == pytest.approx(longitude, abs=1e-6)


async def test_get_location_returns_none_for_an_unknown_id(
    session: AsyncSession,
) -> None:
    result = await service.get_location(session, uuid.uuid4())

    assert result is None


async def test_list_locations_includes_a_newly_created_one(
    session: AsyncSession,
) -> None:
    latitude, longitude = _random_point()
    name = f"test-location-{uuid.uuid4()}"
    created = await service.create_location(
        session, name=name, description=None, latitude=latitude, longitude=longitude
    )

    locations = await service.list_locations(session)

    assert any(location.id == created.id for location in locations)


async def test_find_nearby_finds_a_location_at_the_same_point(
    session: AsyncSession,
) -> None:
    latitude, longitude = _random_point()
    name = f"test-location-{uuid.uuid4()}"
    created = await service.create_location(
        session, name=name, description=None, latitude=latitude, longitude=longitude
    )

    nearby = await service.find_nearby(
        session, latitude=latitude, longitude=longitude, radius_km=1.0
    )

    matches = [n for n in nearby if n.location.id == created.id]
    assert len(matches) == 1
    assert matches[0].distance_km == pytest.approx(0.0, abs=1e-3)


async def test_find_nearby_excludes_a_location_outside_the_radius(
    session: AsyncSession,
) -> None:
    latitude, longitude = _random_point()
    name = f"test-location-{uuid.uuid4()}"
    created = await service.create_location(
        session, name=name, description=None, latitude=latitude, longitude=longitude
    )

    # 2 degrees of longitude is at least ~37km even at the northernmost latitude
    # _random_point() can produce -- far outside a 1km search radius regardless of
    # where the random point landed.
    nearby = await service.find_nearby(
        session, latitude=latitude, longitude=longitude + 2.0, radius_km=1.0
    )

    assert all(n.location.id != created.id for n in nearby)
