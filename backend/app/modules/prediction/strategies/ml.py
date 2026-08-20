"""Heat risk from a trained regression model, served behind the same
PredictionStrategy interface as the baseline strategy.

The model is loaded lazily (on first use, not at import time) and cached on the
instance: importing this module must not require a trained artifact to exist, or
simply importing the prediction module anywhere (tests, tooling) would start failing
whenever nobody has run the training script yet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import joblib

from app.modules.prediction.heat_index import classify_heat_risk
from app.modules.prediction.ml.train import MODEL_VERSION
from app.modules.prediction.schemas import PredictionResult
from app.modules.weather.provider import WeatherProvider


class MLModelNotAvailableError(Exception):
    """No trained model artifact exists at the configured path yet."""


class _Regressor(Protocol):
    def predict(self, features: list[list[float]]) -> Any: ...


class MLHeatRiskStrategy:
    def __init__(self, weather_provider: WeatherProvider, *, model_path: Path) -> None:
        self._weather_provider = weather_provider
        self._model_path = model_path
        self._model: _Regressor | None = None

    def _load_model(self) -> _Regressor:
        if self._model is None:
            if not self._model_path.exists():
                raise MLModelNotAvailableError(
                    f"no trained model at {self._model_path}; run "
                    "`python -m app.modules.prediction.ml.train` first"
                )
            self._model = joblib.load(self._model_path)
        return self._model

    async def predict_heat_risk(
        self, *, latitude: float, longitude: float
    ) -> PredictionResult:
        reading = await self._weather_provider.get_current_weather(
            latitude=latitude, longitude=longitude
        )
        model = self._load_model()
        features = [
            [reading.temperature_c, reading.humidity_percent, reading.wind_speed_kph]
        ]
        heat_index_c = float(model.predict(features)[0])

        return PredictionResult(
            latitude=latitude,
            longitude=longitude,
            temperature_c=reading.temperature_c,
            humidity_percent=reading.humidity_percent,
            heat_index_c=round(heat_index_c, 1),
            risk_level=classify_heat_risk(heat_index_c),
            strategy=f"ml-{MODEL_VERSION}",
            observed_at=reading.observed_at,
        )
