"""enable postgis extension

Revision ID: 69cc0d23cc36
Revises:
Create Date: 2026-08-20 12:23:42.737737

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "69cc0d23cc36"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Spatial data foundation for Phase 5 (GIS module). Enabling the extension here,
    # in its own migration, keeps it independent of any particular domain model's
    # migration history.
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS postgis")
