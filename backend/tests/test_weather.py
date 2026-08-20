from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.weather.dependencies import get_weather_provider
from app.modules.weather.provider import WeatherProviderError
from app.modules.weather.schemas import WeatherReading


class _FakeProvider:
    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        return WeatherReading(
            latitude=latitude,
            longitude=longitude,
            temperature_c=28.0,
            humidity_percent=50.0,
            wind_speed_kph=10.0,
            weather_code=0,
            observed_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
            provider="fake",
        )


class _FailingProvider:
    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        raise WeatherProviderError("upstream is down")


@pytest.fixture
def weather_client(app: FastAPI) -> Iterator[TestClient]:
    app.dependency_overrides[get_weather_provider] = lambda: _FakeProvider()
    with TestClient(app) as test_client:
        yield test_client
    del app.dependency_overrides[get_weather_provider]


def test_current_weather_returns_a_reading(weather_client: TestClient) -> None:
    response = weather_client.get(
        "/api/v1/weather/current", params={"latitude": 12.97, "longitude": 77.59}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["latitude"] == 12.97
    assert body["longitude"] == 77.59
    assert body["provider"] == "fake"


def test_current_weather_rejects_out_of_range_latitude(
    weather_client: TestClient,
) -> None:
    response = weather_client.get(
        "/api/v1/weather/current", params={"latitude": 999, "longitude": 0}
    )

    assert response.status_code == 422


def test_current_weather_requires_latitude_and_longitude(
    weather_client: TestClient,
) -> None:
    response = weather_client.get("/api/v1/weather/current")

    assert response.status_code == 422


def test_current_weather_returns_502_when_the_provider_fails(app: FastAPI) -> None:
    app.dependency_overrides[get_weather_provider] = lambda: _FailingProvider()
    try:
        with TestClient(app) as test_client:
            response = test_client.get(
                "/api/v1/weather/current", params={"latitude": 0, "longitude": 0}
            )
    finally:
        del app.dependency_overrides[get_weather_provider]

    assert response.status_code == 502
