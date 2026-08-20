"""Structured application logging.

Business and infrastructure code call the standard library ``logging`` module and
nothing else — no logger-specific calls scattered through the codebase (CLAUDE.md
section 18: do not couple business logic to a specific logging backend). This module
owns the one place that decides *how* those log records are rendered: JSON with the
active request's correlation ID attached, so log lines from one request can be
reassembled later even after this service is one of several.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from pythonjsonlogger.json import JsonFormatter

from app.core.correlation import get_correlation_id

_CONFIGURED = False


class _CorrelationIdFilter(logging.Filter):
    """Attach the active request's correlation ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id()
        return True


def configure_logging(*, level: str = "INFO", json_output: bool = True) -> None:
    """Configure the root logger. Call once, at process startup.

    Idempotent: safe to call multiple times (for example once per test) without
    stacking duplicate handlers on the root logger.
    """
    global _CONFIGURED

    root = logging.getLogger()
    root.setLevel(level)

    if _CONFIGURED:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.addFilter(_CorrelationIdFilter())

    formatter: logging.Formatter
    if json_output:
        formatter = JsonFormatter(
            "{asctime}{levelname}{name}{message}{correlation_id}",
            style="{",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s [%(correlation_id)s] %(message)s"
        )
    handler.setFormatter(formatter)

    root.handlers = [handler]
    _CONFIGURED = True


def get_logger(name: str, **extra: Any) -> logging.LoggerAdapter[logging.Logger]:
    """Return a logger bound to ``name`` with optional structured extra fields."""
    return logging.LoggerAdapter(logging.getLogger(name), extra=extra)


_UVICORN_LOGGER_NAMES = ("uvicorn", "uvicorn.error", "uvicorn.access")


def align_uvicorn_logging() -> None:
    """Route uvicorn's own log records through the structured root handler.

    When the app runs under ``uvicorn app.main:app``, uvicorn applies its own logging
    config (plain-text handlers on "uvicorn", "uvicorn.error", "uvicorn.access") *after*
    this module is imported and ``configure_logging`` has already run — so without this,
    every access log line silently bypasses structured JSON output and never carries a
    correlation ID, despite CLAUDE.md section 18 requiring both. Call this from the
    application's startup event, which fires after uvicorn's own logging setup.
    """
    for name in _UVICORN_LOGGER_NAMES:
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True
