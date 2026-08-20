"""Password hashing and JWT issuance/verification.

Cross-cutting infrastructure, not auth-domain business logic — it knows nothing about
``User`` or roles, only how to hash a string and how to sign/verify a JWT. That keeps it
reusable by any future module needing tokens (not just ``app.modules.auth``) and keeps
the auth module free of algorithm/library details, which matters if it is ever extracted
into its own service (CLAUDE.md section 39: would this boundary still make sense as an
independent service?).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import Settings

# Argon2id (the argon2-cffi default) is the current OWASP-recommended password hash.
# One process-wide hasher: it is stateless and thread-safe, and constructing it carries
# a small fixed cost that a per-call instance would pay on every login.
_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        _password_hasher.verify(hashed_password, password)
    except (VerifyMismatchError, InvalidHashError):
        return False
    return True


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class InvalidTokenError(Exception):
    """A token failed signature verification, expired, or has the wrong claims."""


def create_token(
    *,
    subject: str,
    token_type: TokenType,
    expires_delta: timedelta,
    settings: Settings,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        # Gives every token a unique identity even when issued in the same second for
        # the same subject and type — useful for future revocation-list support
        # without needing a schema change to add it then.
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(
    token: str, *, expected_type: TokenType, settings: Settings
) -> dict[str, Any]:
    """Decode and validate a token, raising ``InvalidTokenError`` for any failure.

    Callers get one exception type to handle regardless of whether the token was
    malformed, expired, or simply the wrong kind (an access token presented where a
    refresh token was required, or vice versa) — they should not need to know PyJWT's
    exception hierarchy to consume this.
    """
    try:
        claims: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(
            "token is malformed, expired, or has a bad signature"
        ) from exc

    if claims.get("type") != expected_type.value:
        raise InvalidTokenError(f"expected a {expected_type.value} token")

    return claims
