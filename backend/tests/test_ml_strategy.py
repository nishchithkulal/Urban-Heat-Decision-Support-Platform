from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.modules.prediction.heat_index import HeatRiskLevel
from app.modules.prediction.ml.train import (
    generate_training_data,
    save_model,
    train_model,
)
from app.modules.prediction.strategies.ml import (
    MLHeatRiskStrategy,
    MLModelNotAvailableError,
)
from app.modules.weather.schemas import WeatherReading

pytestmark = pytest.mark.anyio


class _FakeWeatherProvider:
    def __init__(self, reading: WeatherReading) -> None:
        self._reading = reading

    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        return self._reading


def _reading(*, temperature_c: float, humidity_percent: float) -> WeatherReading:
    return WeatherReading(
        latitude=0.0,
        longitude=0.0,
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        wind_speed_kph=10.0,
        weather_code=0,
        observed_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
        provider="fake",
    )


@pytest.fixture(scope="module")
def trained_model_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    # A real trained artifact (small sample, fast) shared across this file's tests --
    # this exercises the actual train -> save -> load -> predict path, not a mocked
    # model, while staying fast enough to run on every test invocation.
    data = generate_training_data(sample_count=300, seed=1)
    model, mae = train_model(data, seed=1)
    path = tmp_path_factory.mktemp("ml") / "model.joblib"
    save_model(model, mae=mae, path=path)
    return path


async def test_predict_heat_risk_uses_the_trained_model(
    trained_model_path: Path,
) -> None:
    provider = _FakeWeatherProvider(_reading(temperature_c=38.0, humidity_percent=70.0))
    strategy = MLHeatRiskStrategy(provider, model_path=trained_model_path)

    result = await strategy.predict_heat_risk(latitude=12.97, longitude=77.59)

    assert result.strategy.startswith("ml-")
    assert result.risk_level in (
        HeatRiskLevel.DANGER,
        HeatRiskLevel.EXTREME_DANGER,
        HeatRiskLevel.EXTREME_CAUTION,
    )


async def test_predict_heat_risk_caches_the_loaded_model(
    trained_model_path: Path,
) -> None:
    provider = _FakeWeatherProvider(_reading(temperature_c=25.0, humidity_percent=40.0))
    strategy = MLHeatRiskStrategy(provider, model_path=trained_model_path)

    await strategy.predict_heat_risk(latitude=0.0, longitude=0.0)
    # Delete the file: if the second call reloaded from disk it would fail, proving
    # the first load is cached on the instance rather than repeated per request.
    trained_model_path.unlink()

    await strategy.predict_heat_risk(latitude=0.0, longitude=0.0)


async def test_predict_heat_risk_raises_when_no_model_is_trained(
    tmp_path: Path,
) -> None:
    provider = _FakeWeatherProvider(_reading(temperature_c=25.0, humidity_percent=40.0))
    strategy = MLHeatRiskStrategy(provider, model_path=tmp_path / "missing.joblib")

    with pytest.raises(MLModelNotAvailableError):
        await strategy.predict_heat_risk(latitude=0.0, longitude=0.0)
