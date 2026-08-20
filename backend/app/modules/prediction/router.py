from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.prediction.dependencies import PredictionStrategyDep
from app.modules.prediction.schemas import PredictionResult
from app.modules.weather.provider import WeatherProviderError

router = APIRouter()


@router.get(
    "/heat-risk",
    response_model=PredictionResult,
    summary="Predict current heat risk at a location",
    responses={
        status.HTTP_502_BAD_GATEWAY: {"description": "Upstream provider unavailable"}
    },
)
async def heat_risk(
    strategy: PredictionStrategyDep,
    latitude: Annotated[float, Query(ge=-90, le=90)],
    longitude: Annotated[float, Query(ge=-180, le=180)],
) -> PredictionResult:
    try:
        return await strategy.predict_heat_risk(latitude=latitude, longitude=longitude)
    except WeatherProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to compute a heat risk prediction",
        ) from exc
