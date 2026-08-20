from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.modules.auth.dependencies import require_role
from app.modules.auth.models import Role, User

pytestmark = pytest.mark.anyio


def _user(role: Role) -> User:
    return User(email="rbac@example.com", hashed_password="irrelevant", role=role)


async def test_require_role_allows_a_matching_role() -> None:
    check = require_role(Role.ADMIN)

    result = await check(_user(Role.ADMIN))

    assert result.role is Role.ADMIN


async def test_require_role_allows_any_of_several_roles() -> None:
    check = require_role(Role.ADMIN, Role.USER)

    result = await check(_user(Role.USER))

    assert result.role is Role.USER


async def test_require_role_rejects_a_non_matching_role() -> None:
    check = require_role(Role.ADMIN)

    with pytest.raises(HTTPException) as exc_info:
        await check(_user(Role.USER))

    assert exc_info.value.status_code == 403
