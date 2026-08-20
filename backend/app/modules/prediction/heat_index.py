"""NOAA/National Weather Service heat index ("feels like" temperature).

Reference: https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml

Reproduced faithfully rather than simplified. The Rothfusz regression NWS uses is only
valid/accurate above roughly 80F; below that NWS falls back to a coarser
approximation, and applies further corrections at very low or very high humidity. A
platform whose entire purpose is heat risk cannot afford a casually wrong "feels like"
temperature, so this follows the published algorithm step for step rather than a
simplified approximation of it.
"""

from __future__ import annotations

from enum import StrEnum


def _celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def _fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def heat_index_celsius(*, temperature_c: float, humidity_percent: float) -> float:
    t = _celsius_to_fahrenheit(temperature_c)
    rh = humidity_percent

    simple_hi = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)

    # NWS only applies the full regression once the simple estimate suggests it will
    # actually matter; below that threshold the regression is not calibrated and can
    # produce nonsense.
    if (simple_hi + t) / 2 < 80.0:
        return _fahrenheit_to_celsius(simple_hi)

    hi = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t * t
        - 0.05481717 * rh * rh
        + 0.00122874 * t * t * rh
        + 0.00085282 * t * rh * rh
        - 0.00000199 * t * t * rh * rh
    )

    if rh < 13 and 80 <= t <= 112:
        hi -= ((13 - rh) / 4) * ((17 - abs(t - 95)) / 17) ** 0.5
    elif rh > 85 and 80 <= t <= 87:
        hi += ((rh - 85) / 10) * ((87 - t) / 5)

    return _fahrenheit_to_celsius(hi)


class HeatRiskLevel(StrEnum):
    """NWS heat index risk categories (https://www.weather.gov/safety/heat-index)."""

    LOW = "low"
    CAUTION = "caution"
    EXTREME_CAUTION = "extreme_caution"
    DANGER = "danger"
    EXTREME_DANGER = "extreme_danger"


# NWS category boundaries, published in Fahrenheit (80/90/103/125), converted to
# Celsius here since the rest of this API works in Celsius.
def classify_heat_risk(heat_index_c: float) -> HeatRiskLevel:
    if heat_index_c >= 51.7:
        return HeatRiskLevel.EXTREME_DANGER
    if heat_index_c >= 39.4:
        return HeatRiskLevel.DANGER
    if heat_index_c >= 32.2:
        return HeatRiskLevel.EXTREME_CAUTION
    if heat_index_c >= 26.7:
        return HeatRiskLevel.CAUTION
    return HeatRiskLevel.LOW
