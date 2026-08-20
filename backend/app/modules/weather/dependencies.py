from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.api.deps import HttpClientDep, SettingsDep
from app.modules.weather.provider import WeatherProvider
from app.modules.weather.providers.open_meteo import OpenMeteoProvider


def get_weather_provider(
    client: HttpClientDep, settings: SettingsDep
) -> WeatherProvider:
    return OpenMeteoProvider(client, base_url=settings.weather_provider_base_url)


WeatherProviderDep = Annotated[WeatherProvider, Depends(get_weather_provider)]
