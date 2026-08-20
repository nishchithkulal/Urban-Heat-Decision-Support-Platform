"""Open-Meteo (https://open-meteo.com) weather provider.

Chosen for local development and this portfolio project specifically because it
requires no API key — anyone cloning this repository can run it immediately. A
production deployment wanting SLAs/higher rate limits would add a second
``WeatherProvider`` implementation and select between them in
``dependencies.get_weather_provider``; nothing else in the module would change.
"""

from __future__ import annotations

from datetime import datetime

import httpx
from pydantic import ValidationError

from app.modules.weather.provider import WeatherProviderError
from app.modules.weather.schemas import WeatherReading

_CURRENT_FIELDS = "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"


class OpenMeteoProvider:
    def __init__(self, client: httpx.AsyncClient, *, base_url: str) -> None:
        self._client = client
        self._base_url = base_url

    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        try:
            response = await self._client.get(
                self._base_url,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": _CURRENT_FIELDS,
                },
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            raise WeatherProviderError(
                "failed to reach the upstream weather provider"
            ) from exc

        try:
            current = payload["current"]
            return WeatherReading(
                latitude=latitude,
                longitude=longitude,
                temperature_c=current["temperature_2m"],
                humidity_percent=current["relative_humidity_2m"],
                wind_speed_kph=current["wind_speed_10m"],
                weather_code=current["weather_code"],
                observed_at=datetime.fromisoformat(current["time"]),
                provider="open-meteo",
            )
        except (KeyError, TypeError, ValueError, ValidationError) as exc:
            raise WeatherProviderError(
                "upstream weather provider returned an unexpected payload"
            ) from exc
