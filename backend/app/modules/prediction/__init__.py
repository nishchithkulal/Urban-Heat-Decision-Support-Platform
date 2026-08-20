"""Urban heat risk prediction.

``PredictionStrategy`` (strategy.py) is a ``Protocol``, the same pattern as
``app.modules.weather.provider.WeatherProvider`` -- the baseline heat-index strategy
here and the ML strategy Phase 7 adds both implement it, and the router/dependency
wiring does not change when a second strategy is introduced.
"""
