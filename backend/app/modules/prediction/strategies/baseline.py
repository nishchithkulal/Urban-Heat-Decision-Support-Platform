"""Heat risk from the NWS heat index applied to live weather conditions.

"Baseline" because it is a well-established meteorological formula, not a trained
model -- Phase 7 adds a strategy backed by a real model behind this same
PredictionStrategy interface once there is actual training data to justify one,
rather than jumping straight to ML before the domain is understood (CLAUDE.md
section 10).
"""

from __future__ import annotations

from app.modules.prediction.heat_index import classify_heat_risk, heat_index_celsius
from app.modules.prediction.schemas import PredictionResult
from app.modules.weather.provider import WeatherProvider


class BaselineHeatRiskStrategy:
    def __init__(self, weather_provider: WeatherProvider) -> None:
        self._weather_provider = weather_provider

    async def predict_heat_risk(
        self, *, latitude: float, longitude: float
    ) -> PredictionResult:
        reading = await self._weather_provider.get_current_weather(
            latitude=latitude, longitude=longitude
        )
        heat_index_c = heat_index_celsius(
            temperature_c=reading.temperature_c,
            humidity_percent=reading.humidity_percent,
        )
        return PredictionResult(
            latitude=latitude,
            longitude=longitude,
            temperature_c=reading.temperature_c,
            humidity_percent=reading.humidity_percent,
            heat_index_c=round(heat_index_c, 1),
            risk_level=classify_heat_risk(heat_index_c),
            strategy="baseline-heat-index",
            observed_at=reading.observed_at,
        )
