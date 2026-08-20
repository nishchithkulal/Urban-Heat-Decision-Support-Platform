from __future__ import annotations

import httpx
import pytest

from app.modules.weather.provider import WeatherProviderError
from app.modules.weather.providers.open_meteo import OpenMeteoProvider

pytestmark = pytest.mark.anyio

_BASE_URL = "https://api.open-meteo.example/v1/forecast"

_SUCCESS_PAYLOAD = {
    "current": {
        "time": "2026-08-20T12:00",
        "temperature_2m": 31.4,
        "relative_humidity_2m": 44.0,
        "wind_speed_10m": 12.3,
        "weather_code": 0,
    }
}


def _client(handler: httpx.MockTransport) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=handler)


async def test_get_current_weather_parses_a_successful_response() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        assert request.url.params["latitude"] == "12.97"
        assert request.url.params["longitude"] == "77.59"
        return httpx.Response(200, json=_SUCCESS_PAYLOAD)

    async with _client(httpx.MockTransport(handle)) as client:
        provider = OpenMeteoProvider(client, base_url=_BASE_URL)

        reading = await provider.get_current_weather(latitude=12.97, longitude=77.59)

    assert reading.temperature_c == 31.4
    assert reading.humidity_percent == 44.0
    assert reading.wind_speed_kph == 12.3
    assert reading.weather_code == 0
    assert reading.provider == "open-meteo"


async def test_get_current_weather_raises_on_upstream_error_status() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="service unavailable")

    async with _client(httpx.MockTransport(handle)) as client:
        provider = OpenMeteoProvider(client, base_url=_BASE_URL)

        with pytest.raises(WeatherProviderError):
            await provider.get_current_weather(latitude=12.97, longitude=77.59)


async def test_get_current_weather_raises_on_network_failure() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    async with _client(httpx.MockTransport(handle)) as client:
        provider = OpenMeteoProvider(client, base_url=_BASE_URL)

        with pytest.raises(WeatherProviderError):
            await provider.get_current_weather(latitude=12.97, longitude=77.59)


async def test_get_current_weather_raises_on_malformed_payload() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    async with _client(httpx.MockTransport(handle)) as client:
        provider = OpenMeteoProvider(client, base_url=_BASE_URL)

        with pytest.raises(WeatherProviderError):
            await provider.get_current_weather(latitude=12.97, longitude=77.59)
