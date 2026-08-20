from __future__ import annotations

from datetime import timedelta

import jwt
import pytest

from app.core.config import Settings
from app.core.security import (
    InvalidTokenError,
    TokenType,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hashed_password_is_not_the_plaintext() -> None:
    hashed = hash_password("correct horse battery staple")

    assert hashed != "correct horse battery staple"


def test_verify_password_accepts_the_correct_password() -> None:
    hashed = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", hashed) is True


def test_verify_password_rejects_the_wrong_password() -> None:
    hashed = hash_password("correct horse battery staple")

    assert verify_password("wrong password", hashed) is False


def test_create_and_decode_token_round_trips(settings: Settings) -> None:
    token = create_token(
        subject="user-123",
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=5),
        settings=settings,
    )

    claims = decode_token(token, expected_type=TokenType.ACCESS, settings=settings)

    assert claims["sub"] == "user-123"
    assert claims["type"] == "access"


def test_decode_token_rejects_the_wrong_token_type(settings: Settings) -> None:
    refresh_token = create_token(
        subject="user-123",
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=1),
        settings=settings,
    )

    with pytest.raises(InvalidTokenError):
        decode_token(refresh_token, expected_type=TokenType.ACCESS, settings=settings)


def test_decode_token_rejects_an_expired_token(settings: Settings) -> None:
    token = create_token(
        subject="user-123",
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=-1),
        settings=settings,
    )

    with pytest.raises(InvalidTokenError):
        decode_token(token, expected_type=TokenType.ACCESS, settings=settings)


def test_decode_token_rejects_a_bad_signature(settings: Settings) -> None:
    token = create_token(
        subject="user-123",
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=5),
        settings=settings,
    )
    forged = jwt.encode(
        jwt.decode(token, options={"verify_signature": False}),
        "a-completely-different-signing-secret-value",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_token(forged, expected_type=TokenType.ACCESS, settings=settings)
