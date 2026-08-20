from __future__ import annotations

import pytest

from app.modules.prediction.heat_index import (
    HeatRiskLevel,
    classify_heat_risk,
    heat_index_celsius,
)


def _f_to_c(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def test_heat_index_matches_the_published_nws_reference_example() -> None:
    # https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml: T=96F, RH=65% is
    # NWS's own worked example, published as HI=121F.
    result_c = heat_index_celsius(temperature_c=_f_to_c(96), humidity_percent=65)

    assert result_c * 9 / 5 + 32 == pytest.approx(121, abs=0.2)


def test_heat_index_falls_back_to_the_simple_formula_at_mild_conditions() -> None:
    # Well below the 80F threshold where the full regression applies -- the result
    # should stay close to the actual temperature, not diverge wildly.
    result_c = heat_index_celsius(temperature_c=20.0, humidity_percent=40)

    assert result_c == pytest.approx(20.0, abs=3.0)


@pytest.mark.parametrize(
    ("heat_index_c", "expected"),
    [
        (10.0, HeatRiskLevel.LOW),
        (26.6, HeatRiskLevel.LOW),
        (26.7, HeatRiskLevel.CAUTION),
        (32.1, HeatRiskLevel.CAUTION),
        (32.2, HeatRiskLevel.EXTREME_CAUTION),
        (39.3, HeatRiskLevel.EXTREME_CAUTION),
        (39.4, HeatRiskLevel.DANGER),
        (51.6, HeatRiskLevel.DANGER),
        (51.7, HeatRiskLevel.EXTREME_DANGER),
        (60.0, HeatRiskLevel.EXTREME_DANGER),
    ],
)
def test_classify_heat_risk_boundaries(
    heat_index_c: float, expected: HeatRiskLevel
) -> None:
    assert classify_heat_risk(heat_index_c) is expected
