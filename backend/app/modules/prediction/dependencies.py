from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import Depends

from app.api.deps import SettingsDep
from app.core.config import PredictionStrategyName
from app.modules.prediction.strategies.baseline import BaselineHeatRiskStrategy
from app.modules.prediction.strategies.ml import MLHeatRiskStrategy
from app.modules.prediction.strategy import PredictionStrategy
from app.modules.weather.dependencies import WeatherProviderDep


def get_prediction_strategy(
    weather_provider: WeatherProviderDep, settings: SettingsDep
) -> PredictionStrategy:
    if settings.prediction_strategy is PredictionStrategyName.ML:
        return MLHeatRiskStrategy(
            weather_provider, model_path=Path(settings.ml_model_path)
        )
    return BaselineHeatRiskStrategy(weather_provider)


PredictionStrategyDep = Annotated[PredictionStrategy, Depends(get_prediction_strategy)]
