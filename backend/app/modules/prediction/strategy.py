from __future__ import annotations

from typing import Protocol

from app.modules.prediction.schemas import PredictionResult


class PredictionStrategy(Protocol):
    async def predict_heat_risk(
        self, *, latitude: float, longitude: float
    ) -> PredictionResult: ...
