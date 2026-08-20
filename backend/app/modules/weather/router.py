from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.weather.dependencies import WeatherProviderDep
from app.modules.weather.provider import WeatherProviderError
from app.modules.weather.schemas import WeatherReading

router = APIRouter()


@router.get(
    "/current",
    response_model=WeatherReading,
    summary="Get current weather conditions at a location",
    responses={
        status.HTTP_502_BAD_GATEWAY: {"description": "Upstream provider unavailable"}
    },
)
async def current_weather(
    provider: WeatherProviderDep,
    latitude: Annotated[float, Query(ge=-90, le=90)],
    longitude: Annotated[float, Query(ge=-180, le=180)],
) -> WeatherReading:
    try:
        return await provider.get_current_weather(
            latitude=latitude, longitude=longitude
        )
    except WeatherProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve weather data from the upstream provider",
        ) from exc
