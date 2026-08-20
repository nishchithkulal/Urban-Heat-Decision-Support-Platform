from __future__ import annotations

from app.core.config import PredictionStrategyName, Settings
from app.modules.prediction.dependencies import get_prediction_strategy
from app.modules.prediction.strategies.baseline import BaselineHeatRiskStrategy
from app.modules.prediction.strategies.ml import MLHeatRiskStrategy
from app.modules.weather.schemas import WeatherReading


class _FakeWeatherProvider:
    async def get_current_weather(
        self, *, latitude: float, longitude: float
    ) -> WeatherReading:
        raise NotImplementedError


def test_get_prediction_strategy_returns_baseline_by_default(
    settings: Settings,
) -> None:
    strategy = get_prediction_strategy(_FakeWeatherProvider(), settings)

    assert isinstance(strategy, BaselineHeatRiskStrategy)


def test_get_prediction_strategy_returns_ml_when_configured(settings: Settings) -> None:
    ml_settings = settings.model_copy(
        update={"prediction_strategy": PredictionStrategyName.ML}
    )

    strategy = get_prediction_strategy(_FakeWeatherProvider(), ml_settings)

    assert isinstance(strategy, MLHeatRiskStrategy)
