"""Aggregation point for all versioned API routes.

Each domain module (app.modules.<name>) owns its own router and is included here. This
file should only ever grow ``include_router`` calls — it must not accumulate business
logic or per-module knowledge beyond "where does this module's router live".
"""

from __future__ import annotations

from fastapi import APIRouter

from app.modules.auth.router import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
