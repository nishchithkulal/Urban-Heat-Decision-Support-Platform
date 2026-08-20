"""Shared FastAPI dependencies.

Route handlers depend on ``SettingsDep`` rather than calling ``get_settings()``
directly, so tests can override configuration per-test via
``app.dependency_overrides`` instead of monkeypatching the environment.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_http_client(request: Request) -> httpx.AsyncClient:
    """Return the app-wide pooled HTTP client for calling external services.

    One client per app instance (see ``app/main.py``), not one per request: httpx
    pools connections internally, so a fresh client per call would reconnect (and
    re-do TLS) on every outbound request instead of reusing keep-alive connections.
    """
    return request.app.state.http_client  # type: ignore[no-any-return]


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]


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
