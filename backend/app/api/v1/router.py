"""Aggregation point for all versioned API routes.

Each domain module (app.modules.<name>) owns its own router and is included here. This
file should only ever grow ``include_router`` calls — it must not accumulate business
logic or per-module knowledge beyond "where does this module's router live".
"""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.gis.router import router as gis_router
from app.modules.prediction.router import router as prediction_router
from app.modules.weather.router import router as weather_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(weather_router, prefix="/weather", tags=["Weather"])
router.include_router(gis_router, prefix="/gis", tags=["GIS"])
router.include_router(prediction_router, prefix="/predictions", tags=["Predictions"])
