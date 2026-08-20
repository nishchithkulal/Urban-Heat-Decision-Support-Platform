from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import DbSessionDep
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import Role
from app.modules.gis import service
from app.modules.gis.models import Location
from app.modules.gis.schemas import LocationCreate, LocationRead, NearbyLocationRead

router = APIRouter()


def _to_read(location: Location) -> LocationRead:
    latitude, longitude = service.coordinates_of(location)
    return LocationRead(
        id=location.id,
        name=location.name,
        description=location.description,
        latitude=latitude,
        longitude=longitude,
        created_at=location.created_at,
    )


@router.post(
    "/locations",
    response_model=LocationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new location",
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def create_location(payload: LocationCreate, db: DbSessionDep) -> LocationRead:
    location = await service.create_location(
        db,
        name=payload.name,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    return _to_read(location)


@router.get(
    "/locations/nearby",
    response_model=list[NearbyLocationRead],
    summary="Find registered locations within a radius of a point",
)
async def nearby_locations(
    db: DbSessionDep,
    latitude: Annotated[float, Query(ge=-90, le=90)],
    longitude: Annotated[float, Query(ge=-180, le=180)],
    radius_km: Annotated[float, Query(gt=0, le=500)] = 10.0,
) -> list[NearbyLocationRead]:
    nearby = await service.find_nearby(
        db, latitude=latitude, longitude=longitude, radius_km=radius_km
    )
    return [
        NearbyLocationRead(
            **_to_read(n.location).model_dump(), distance_km=n.distance_km
        )
        for n in nearby
    ]


@router.get(
    "/locations", response_model=list[LocationRead], summary="List all locations"
)
async def list_locations(db: DbSessionDep) -> list[LocationRead]:
    locations = await service.list_locations(db)
    return [_to_read(location) for location in locations]


@router.get(
    "/locations/{location_id}",
    response_model=LocationRead,
    summary="Get a single location",
)
async def get_location(location_id: uuid.UUID, db: DbSessionDep) -> LocationRead:
    location = await service.get_location(db, location_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return _to_read(location)
