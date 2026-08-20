"""Auth domain logic. Route handlers stay thin and call into here (CLAUDE.md
section 14) rather than embedding queries and password checks directly in
``router.py``.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.modules.auth.models import Role, User


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await session.get(User, user_id)


async def register_user(session: AsyncSession, *, email: str, password: str) -> User:
    if await get_user_by_email(session, email) is not None:
        raise EmailAlreadyRegisteredError(email)

    user = User(email=email, hashed_password=hash_password(password), role=Role.USER)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession, *, email: str, password: str
) -> User:
    user = await get_user_by_email(session, email)
    # Same InvalidCredentialsError whether the email doesn't exist or the password is
    # wrong — distinguishing the two in the response would let an attacker enumerate
    # registered emails.
    if user is None or not user.is_active:
        raise InvalidCredentialsError()
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
    return user
