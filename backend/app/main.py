"""Application composition root.

Built with an app factory (``create_app``) rather than a module-level ``app`` instance.
A module-level ``app`` bakes in configuration at import time, which makes it impossible
for tests to build an isolated app with overridden settings — they would have to
monkeypatch the environment before the module is first imported, and every test module
sharing the process would then fight over global state.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.router import router as v1_router
from app.core.config import Settings, get_settings
from app.core.correlation import CorrelationIdMiddleware
from app.core.database import create_engine, create_session_factory
from app.core.errors import register_exception_handlers
from app.core.logging import align_uvicorn_logging, configure_logging


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Runs after uvicorn has applied its own logging config, so this reliably wins
    # regardless of whether the app is served by uvicorn, run directly in tests, or
    # imported some other way.
    align_uvicorn_logging()
    try:
        yield
    finally:
        await app.state.db_engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and configure a FastAPI application instance.

    Args:
        settings: Override for testing. Defaults to the process-wide cached settings.
    """
    settings = settings or get_settings()
    configure_logging(level=settings.log_level, json_output=settings.log_json)

    app = FastAPI(
        title=settings.project_name,
        description="AI-powered Urban Heat Decision Support Platform",
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        contact={"name": "HeatPilot AI Team"},
        lifespan=_lifespan,
    )

    engine = create_engine(settings)
    app.state.db_engine = engine
    app.state.db_session_factory = create_session_factory(engine)

    # Correlation ID must be outermost so it wraps CORS handling and every response,
    # including error responses produced by the exception handlers below.
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
