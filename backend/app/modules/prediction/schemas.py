from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.prediction.heat_index import HeatRiskLevel


class PredictionResult(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    temperature_c: float
    humidity_percent: float
    heat_index_c: float
    risk_level: HeatRiskLevel
    # Which PredictionStrategy produced this result, e.g. "baseline-heat-index" or
    # (Phase 7) a model identifier -- lets API consumers distinguish predictions once
    # more than one strategy exists.
    strategy: str
    observed_at: datetime
