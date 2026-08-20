"""FastAPI dependencies for authenticated/authorized routes.

Lives in the auth module rather than ``app.api.deps`` (which only holds
module-agnostic dependencies like settings and the raw DB session) because these
depend on auth's own token format and ``User``/``Role`` — another module protecting
its routes imports ``CurrentUserDep`` or ``require_role`` from here, the same way it
would call a client if auth were an independent service.
"""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.deps import DbSessionDep, SettingsDep
from app.core.security import InvalidTokenError, TokenType, decode_token
from app.modules.auth import service
from app.modules.auth.models import Role, User

# tokenUrl is relative to the OpenAPI schema's root, used only to populate Swagger
# UI's "Authorize" flow — it does not affect how tokens are actually validated below.
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
    db: DbSessionDep,
    settings: SettingsDep,
) -> User:
    try:
        claims = decode_token(token, expected_type=TokenType.ACCESS, settings=settings)
        user_id = uuid.UUID(str(claims["sub"]))
    except (InvalidTokenError, KeyError, ValueError) as exc:
        raise _CREDENTIALS_ERROR from exc

    user = await service.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_ERROR
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_role(*allowed: Role) -> Callable[[User], Awaitable[User]]:
    """Build a dependency that 403s unless the current user has one of ``allowed``.

    A factory rather than a single dependency because "which roles" varies per route;
    ``Depends(require_role(Role.ADMIN))`` reads at the call site as exactly the
    permission being enforced.
    """

    async def _check(current_user: CurrentUserDep) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return _check
