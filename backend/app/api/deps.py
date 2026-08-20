"""Shared FastAPI dependencies.

Route handlers depend on ``SettingsDep`` rather than calling ``get_settings()``
directly, so tests can override configuration per-test via
``app.dependency_overrides`` instead of monkeypatching the environment.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
