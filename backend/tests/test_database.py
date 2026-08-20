from __future__ import annotations

import pytest
from sqlalchemy import text

from app.core.config import Settings
from app.core.database import create_engine, create_session_factory

pytestmark = pytest.mark.anyio


async def test_session_factory_executes_a_query_against_a_real_database(
    settings: Settings,
) -> None:
    engine = create_engine(settings)
    try:
        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar_one() == 1
    finally:
        await engine.dispose()


async def test_postgis_extension_is_enabled(settings: Settings) -> None:
    # Guards against a migration regression: if a future change to the enable-postgis
    # migration (or the migration order) silently stops applying it, this fails loudly
    # instead of Phase 5's spatial queries failing later with a cryptic SQL error.
    engine = create_engine(settings)
    try:
        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            result = await session.execute(text("SELECT PostGIS_Version()"))
            assert result.scalar_one() is not None
    finally:
        await engine.dispose()
