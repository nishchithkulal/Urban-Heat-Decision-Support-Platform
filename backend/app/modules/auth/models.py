"""ORM models owned by the auth module.

Other modules must not query these tables directly — go through
``app.modules.auth.service`` (CLAUDE.md section 7: avoid importing another module's
database internals directly). That is what lets auth become its own service later
without every other module needing a rewrite, just a client for whatever API auth
exposes instead.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(
        # values_callable: without it, SQLAlchemy uses the enum *member names*
        # ("USER", "ADMIN") as the Postgres enum labels, not Role's own string values
        # ("user", "admin") — which would mismatch server_default below and every
        # other place in the codebase that compares against Role.USER.value.
        SAEnum(
            Role, name="user_role", values_callable=lambda enum: [e.value for e in enum]
        ),
        default=Role.USER,
        server_default=Role.USER.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
