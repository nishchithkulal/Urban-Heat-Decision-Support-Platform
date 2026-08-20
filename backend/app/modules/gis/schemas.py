from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    latitude: float
    longitude: float
    created_at: datetime


class NearbyLocationRead(LocationRead):
    distance_km: float
