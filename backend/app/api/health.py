"""Liveness and readiness probes.

Deliberately unversioned and outside ``/api/v1``: these are infrastructure contracts
consumed by an orchestrator's health checks, not part of the public API surface, and
they must not move if the API is ever re-versioned.

The two endpoints answer different questions and must stay different:

* ``/livez`` — is the process alive? Checks nothing beyond that. This is what an
  orchestrator uses to decide whether to kill and restart the container.
* ``/readyz`` — can this instance currently serve traffic? Checks dependencies. This is
  what an orchestrator uses to decide whether to route traffic to it.

Collapsing them into one ``/health`` endpoint that checks the database means a brief
database blip makes the orchestrator conclude the *process* is broken and kill it too —
turning a transient dependency hiccup into a full restart storm.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbSessionDep

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])


class HealthStatus(BaseModel):
    status: str


@router.get(
    "/livez",
    summary="Liveness probe",
    description="Returns 200 if the process is running. Checks no dependencies.",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
)
def liveness() -> HealthStatus:
    return HealthStatus(status="alive")


@router.get(
    "/readyz",
    summary="Readiness probe",
    description=(
        "Returns 200 if this instance can currently serve traffic, 503 if a "
        "dependency (currently: the database) is unreachable."
    ),
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Not ready"}},
)
async def readiness(db: DbSessionDep) -> HealthStatus:
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("Readiness check failed: database unavailable", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return HealthStatus(status="ready")
