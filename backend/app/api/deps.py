"""Shared FastAPI dependencies.

Route handlers depend on ``SettingsDep`` rather than calling ``get_settings()``
directly, so tests can override configuration per-test via
``app.dependency_overrides`` instead of monkeypatching the environment.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped session from the app's session factory.

    Reads the session factory off ``request.app.state`` rather than a module-level
    singleton so each app instance (one per ``Settings`` in tests, see
    ``app/main.py``) gets sessions bound to its own engine.
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
