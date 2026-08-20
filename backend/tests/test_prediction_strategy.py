from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.prediction.heat_index import HeatRiskLevel
from app.modules.prediction.strategies.baseline import BaselineHeatRiskStrategy
from app.modules.weather.provider import WeatherProviderError
from app.modules.weather.schemas import WeatherReading

pytestmark = pytest.mark.anyio


class _FakeWeatherProvider:
    def __init__(self, reading: WeatherReading) -> None:
        self._reading = reading

    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        return self._reading


class _FailingWeatherProvider:
    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        raise WeatherProviderError("upstream is down")


def _reading(*, temperature_c: float, humidity_percent: float) -> WeatherReading:
    return WeatherReading(
        latitude=0.0,
        longitude=0.0,
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        wind_speed_kph=0.0,
        weather_code=0,
        observed_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
        provider="fake",
    )


async def test_predict_heat_risk_computes_the_heat_index_from_live_weather() -> None:
    provider = _FakeWeatherProvider(_reading(temperature_c=35.6, humidity_percent=65.0))
    strategy = BaselineHeatRiskStrategy(provider)

    result = await strategy.predict_heat_risk(latitude=12.97, longitude=77.59)

    assert result.temperature_c == 35.6
    assert result.humidity_percent == 65.0
    assert result.heat_index_c > result.temperature_c
    assert result.risk_level in (HeatRiskLevel.DANGER, HeatRiskLevel.EXTREME_DANGER)
    assert result.strategy == "baseline-heat-index"


async def test_predict_heat_risk_reports_low_risk_in_mild_conditions() -> None:
    provider = _FakeWeatherProvider(_reading(temperature_c=15.0, humidity_percent=50.0))
    strategy = BaselineHeatRiskStrategy(provider)

    result = await strategy.predict_heat_risk(latitude=51.5, longitude=-0.1)

    assert result.risk_level is HeatRiskLevel.LOW


async def test_predict_heat_risk_propagates_weather_provider_errors() -> None:
    strategy = BaselineHeatRiskStrategy(_FailingWeatherProvider())

    with pytest.raises(WeatherProviderError):
        await strategy.predict_heat_risk(latitude=0.0, longitude=0.0)
