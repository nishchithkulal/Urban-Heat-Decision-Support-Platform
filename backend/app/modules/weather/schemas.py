from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WeatherReading(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    temperature_c: float
    humidity_percent: float
    wind_speed_kph: float
    # WMO weather interpretation code (https://open-meteo.com/en/docs), e.g. 0 = clear
    # sky, 61 = slight rain. Kept as the provider's raw code rather than translated to
    # a label here — that mapping is a presentation concern for whichever consumer
    # (this API's clients, eventually the frontend) wants to render it.
    weather_code: int
    observed_at: datetime
    provider: str
