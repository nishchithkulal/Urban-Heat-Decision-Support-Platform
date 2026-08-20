"""Aggregation point for all versioned API routes.

Each domain module (app.modules.<name>) owns its own router and is included here. This
file should only ever grow ``include_router`` calls — it must not accumulate business
logic or per-module knowledge beyond "where does this module's router live".
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# No domain modules exist yet (Phase 1 is foundation only). The first module router
# is included here, e.g.:
#
#   from app.modules.weather.router import router as weather_router
#   router.include_router(weather_router, prefix="/weather", tags=["Weather"])
