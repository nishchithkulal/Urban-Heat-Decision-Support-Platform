"""add locations table

Revision ID: 5bb3219d04f8
Revises: 0eef04ce3c1a
Create Date: 2026-08-20 12:47:54.612368

"""

from __future__ import annotations

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5bb3219d04f8"
down_revision: str | Sequence[str] | None = "0eef04ce3c1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geography(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeogFromText",
                name="geography",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # No explicit index on `geom`: GeoAlchemy2's DDL event listener creates the GiST
    # index automatically when the Geography column is created (the column's default
    # spatial_index=True). Autogenerate proposes idx_locations_geom too, not knowing
    # that -- creating it here would collide with the one GeoAlchemy2 already made.
    op.create_index(op.f("ix_locations_name"), "locations", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_locations_name"), table_name="locations")
    op.drop_table("locations")
