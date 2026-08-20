"""The weather module's boundary to the outside world.

``WeatherProvider`` is a ``Protocol`` (structural typing, no inheritance required)
rather than an abstract base class, so a test double only needs to implement
``get_current_weather`` — it does not need to subclass anything from this module.
Swapping the upstream weather API later (or adding a second provider and picking
between them) means writing a new class that satisfies this protocol; nothing calling
it through ``WeatherProviderDep`` needs to change (CLAUDE.md section 39: this is the
seam a future standalone weather service would be extracted along).
"""

from __future__ import annotations

from typing import Protocol

from app.modules.weather.schemas import WeatherReading


class WeatherProviderError(Exception):
    """The upstream provider could not be reached or returned an unusable payload."""


class WeatherProvider(Protocol):
    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading: ...
