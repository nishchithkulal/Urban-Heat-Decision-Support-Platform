"""Training and serialization for the ML heat-risk prediction strategy.

Separate from ``strategies/`` (which holds request-time ``PredictionStrategy``
implementations): this package is a build-time concern, run offline via
``python -m app.modules.prediction.ml.train`` to produce the artifact
``strategies/ml.py`` loads at serve time. It has no FastAPI dependency and is never
imported by the request path except to load the finished artifact.
"""
