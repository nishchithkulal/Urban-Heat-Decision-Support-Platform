from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.modules.prediction.strategies.baseline import BaselineHeatRiskStrategy
from app.modules.prediction.strategy import PredictionStrategy
from app.modules.weather.dependencies import WeatherProviderDep


def get_prediction_strategy(
    weather_provider: WeatherProviderDep,
) -> PredictionStrategy:
    return BaselineHeatRiskStrategy(weather_provider)


PredictionStrategyDep = Annotated[PredictionStrategy, Depends(get_prediction_strategy)]
