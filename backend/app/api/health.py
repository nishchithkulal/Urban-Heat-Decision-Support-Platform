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

from fastapi import APIRouter, status
from pydantic import BaseModel

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
        "Returns 200 if this instance can currently serve traffic. "
        "Will check dependencies (database, etc.) once they exist."
    ),
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
)
def readiness() -> HealthStatus:
    # No dependencies exist yet (Phase 1: no database, no cache). This will gain real
    # dependency checks in Phase 2 rather than being retrofitted from scratch.
    return HealthStatus(status="ready")
