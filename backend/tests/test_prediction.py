from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.modules.prediction.dependencies import get_prediction_strategy
from app.modules.prediction.heat_index import HeatRiskLevel
from app.modules.prediction.schemas import PredictionResult
from app.modules.weather.provider import WeatherProviderError


class _FakeStrategy:
    async def predict_heat_risk(
        self, *, latitude: float, longitude: float
    ) -> PredictionResult:
        return PredictionResult(
            latitude=latitude,
            longitude=longitude,
            temperature_c=40.0,
            humidity_percent=60.0,
            heat_index_c=45.0,
            risk_level=HeatRiskLevel.DANGER,
            strategy="fake",
            observed_at=datetime(2026, 8, 20, 12, 0, tzinfo=UTC),
        )


class _FailingStrategy:
    async def predict_heat_risk(
        self, *, latitude: float, longitude: float
    ) -> PredictionResult:
        raise WeatherProviderError("upstream is down")


@pytest.fixture
def prediction_client(app: FastAPI) -> Iterator[TestClient]:
    app.dependency_overrides[get_prediction_strategy] = lambda: _FakeStrategy()
    with TestClient(app) as test_client:
        yield test_client
    del app.dependency_overrides[get_prediction_strategy]


def test_heat_risk_returns_a_prediction(prediction_client: TestClient) -> None:
    response = prediction_client.get(
        "/api/v1/predictions/heat-risk", params={"latitude": 12.97, "longitude": 77.59}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["risk_level"] == "danger"
    assert body["strategy"] == "fake"


def test_heat_risk_rejects_out_of_range_latitude(prediction_client: TestClient) -> None:
    response = prediction_client.get(
        "/api/v1/predictions/heat-risk", params={"latitude": 999, "longitude": 0}
    )

    assert response.status_code == 422


def test_heat_risk_returns_502_when_the_strategy_fails(app: FastAPI) -> None:
    app.dependency_overrides[get_prediction_strategy] = lambda: _FailingStrategy()
    try:
        with TestClient(app) as test_client:
            response = test_client.get(
                "/api/v1/predictions/heat-risk", params={"latitude": 0, "longitude": 0}
            )
    finally:
        del app.dependency_overrides[get_prediction_strategy]

    assert response.status_code == 502
