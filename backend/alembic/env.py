import asyncio
from logging.config import fileConfig
from typing import Any

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.config import get_settings
from app.core.database import Base

# Each domain module's models must be imported somewhere before Base.metadata is read,
# or its tables are invisible to `alembic revision --autogenerate`. This is that one
# place — add a line here whenever a module gains models, no other file needs to know.
from app.modules.auth import models as auth_models  # noqa: E402,F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Single source of truth for the connection string: HEATPILOT_DATABASE_URL via the
# same Settings the app runtime uses, rather than a second URL hardcoded in
# alembic.ini that can silently drift from it.
config.set_main_option("sqlalchemy.url", get_settings().database_url)

# Domain modules import Base from app.core.database, so importing it here (once
# domain models exist) makes their tables visible to `alembic revision --autogenerate`
# without this file needing to know which modules exist.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# The postgis/postgis Docker image (and any Postgres with the tiger_geocoder/topology
# extensions installed) pre-creates dozens of tables that belong to those extensions,
# not this application. Without this filter, every `alembic revision --autogenerate`
# would propose dropping all of them, because they exist in the database but are not
# part of our declarative metadata. This list is the stable, documented set of tables
# those two extensions install; it does not need to change unless a future migration
# deliberately enables another PostGIS extension with its own tables.
_POSTGIS_EXTENSION_TABLES = frozenset(
    {
        "spatial_ref_sys",
        "topology",
        "layer",
        "addr",
        "addrfeat",
        "bg",
        "county",
        "county_lookup",
        "countysub_lookup",
        "cousub",
        "direction_lookup",
        "edges",
        "faces",
        "featnames",
        "geocode_settings",
        "geocode_settings_default",
        "loader_lookuptables",
        "loader_platform",
        "loader_variables",
        "pagc_gaz",
        "pagc_lex",
        "pagc_rules",
        "place",
        "place_lookup",
        "secondary_unit_lookup",
        "state",
        "state_lookup",
        "street_type_lookup",
        "tabblock",
        "tabblock20",
        "tract",
        "zcta5",
        "zip_lookup",
        "zip_lookup_all",
        "zip_lookup_base",
        "zip_state",
        "zip_state_loc",
    }
)


def _include_object(
    object_: Any, name: str | None, type_: str, reflected: bool, compare_to: Any
) -> bool:
    if type_ == "table" and reflected and compare_to is None:
        return name not in _POSTGIS_EXTENSION_TABLES
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=_include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=_include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
