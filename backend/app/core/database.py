"""Async database engine, session factory, and declarative base.

The engine and session factory are per-application-instance state (stored on
``app.state``) rather than module-level singletons. ``create_app`` already accepts a
``Settings`` override for test isolation (see ``app/main.py``); a module-level engine
would defeat that by binding every app instance to whichever ``DATABASE_URL`` first
imported this module.

Domain models live in their own modules (``app.modules.<name>.models``) and import
``Base`` from here so ``Base.metadata`` accumulates every table for Alembic
autogeneration, without this module needing to know which domain modules exist.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import Settings


class Base(DeclarativeBase):
    """Declarative base shared by every ORM model in the application."""


def create_engine(settings: Settings) -> AsyncEngine:
    """Build the async engine for one application instance.

    ``pool_pre_ping`` trades a small per-checkout latency cost for not handing
    request handlers a dead connection after the database restarts or a load
    balancer drops an idle connection.
    """
    return create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: FastAPI serializes the response after the request
    # handler (and its session) has returned. Expiring attributes on commit would
    # make already-fetched values raise on access outside the session's lifetime.
    return async_sessionmaker(engine, expire_on_commit=False)
