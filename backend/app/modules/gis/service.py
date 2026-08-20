"""GIS domain logic. Every spatial computation here goes through PostGIS functions
(``ST_DWithin``, ``ST_Distance``, ...) rather than being reimplemented in Python --
CLAUDE.md section 16: GIS-specific functionality should use PostGIS rather than
attempting to reproduce spatial operations in application code. Reimplementing
great-circle distance in Python would be slower, error-prone, and unable to use the
spatial index PostGIS maintains on the geography column.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_MakePoint, ST_SetSRID
from geoalchemy2.shape import to_shape
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.gis.models import Location


@dataclass(frozen=True)
class NearbyLocation:
    location: Location
    distance_km: float


def _point(*, latitude: float, longitude: float) -> WKTElement:
    # WKT point order is (longitude, latitude) -- (x, y) -- the opposite of how
    # coordinates are usually spoken/written. Getting this backwards silently places
    # points on the wrong side of the equator/prime meridian instead of raising.
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


def coordinates_of(location: Location) -> tuple[float, float]:
    """Return (latitude, longitude) for a persisted Location."""
    point = to_shape(location.geom)
    return point.y, point.x


async def create_location(
    session: AsyncSession,
    *,
    name: str,
    description: str | None,
    latitude: float,
    longitude: float,
) -> Location:
    location = Location(
        name=name,
        description=description,
        geom=_point(latitude=latitude, longitude=longitude),
    )
    session.add(location)
    await session.commit()
    await session.refresh(location)
    return location


async def get_location(
    session: AsyncSession, location_id: uuid.UUID
) -> Location | None:
    return await session.get(Location, location_id)


async def list_locations(session: AsyncSession) -> list[Location]:
    result = await session.execute(select(Location).order_by(Location.name))
    return list(result.scalars())


async def find_nearby(
    session: AsyncSession, *, latitude: float, longitude: float, radius_km: float
) -> list[NearbyLocation]:
    origin = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
    distance_m = ST_Distance(Location.geom, origin)
    stmt = (
        select(Location, distance_m.label("distance_m"))
        .where(ST_DWithin(Location.geom, origin, radius_km * 1000))
        .order_by(distance_m)
    )
    result = await session.execute(stmt)
    return [
        NearbyLocation(location=row.Location, distance_km=row.distance_m / 1000)
        for row in result
    ]
