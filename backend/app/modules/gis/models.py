from __future__ import annotations

import uuid
from datetime import datetime

from geoalchemy2 import Geography
from geoalchemy2.elements import WKBElement
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Location(Base):
    """A named point of interest: a monitoring station, neighborhood centroid, or any
    other place the platform tracks heat data for. Predictions (Phase 6+) will be
    computed per-location rather than for arbitrary coordinates.
    """

    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), index=True)
    description: Mapped[str | None] = mapped_column(String(1000), default=None)
    # Read back as a WKBElement; writes accept a WKTElement (see service._point) --
    # GeoAlchemy2/PostGIS handle that conversion, mypy just needs the read-side type.
    geom: Mapped[WKBElement] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
