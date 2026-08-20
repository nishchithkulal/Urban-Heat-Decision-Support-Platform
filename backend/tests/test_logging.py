from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging import _UVICORN_LOGGER_NAMES


def test_startup_strips_uvicorns_own_log_handlers(app: FastAPI) -> None:
    # Simulate uvicorn having already attached its own plain-text handlers, as it does
    # in the real deployment (after this module is imported, before requests are
    # served). Startup should strip them so records flow to our root handler instead.
    for name in _UVICORN_LOGGER_NAMES:
        logger = logging.getLogger(name)
        logger.addHandler(logging.NullHandler())
        logger.propagate = False

    with TestClient(app):
        pass

    for name in _UVICORN_LOGGER_NAMES:
        logger = logging.getLogger(name)
        assert logger.handlers == []
        assert logger.propagate is True
