from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSessionDep, SettingsDep
from app.core.config import Settings
from app.core.security import InvalidTokenError, TokenType, create_token, decode_token
from app.modules.auth import service
from app.modules.auth.dependencies import CurrentUserDep
from app.modules.auth.models import User
from app.modules.auth.schemas import RefreshRequest, TokenPair, UserCreate, UserRead

router = APIRouter()


def _issue_token_pair(*, user: User, settings: Settings) -> TokenPair:
    subject = str(user.id)
    access_token = create_token(
        subject=subject,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        settings=settings,
    )
    refresh_token = create_token(
        subject=subject,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        settings=settings,
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account",
)
async def register(payload: UserCreate, db: DbSessionDep) -> User:
    try:
        return await service.register_user(
            db, email=payload.email, password=payload.password
        )
    except service.EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from exc


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Exchange email/password for an access and refresh token",
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSessionDep,
    settings: SettingsDep,
) -> TokenPair:
    # OAuth2PasswordRequestForm's field is named `username` by spec; this API treats
    # it as the account's email.
    try:
        user = await service.authenticate_user(
            db, email=form_data.username, password=form_data.password
        )
    except service.InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return _issue_token_pair(user=user, settings=settings)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Exchange a refresh token for a new token pair",
)
async def refresh(
    payload: RefreshRequest, db: DbSessionDep, settings: SettingsDep
) -> TokenPair:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
    )
    try:
        claims = decode_token(
            payload.refresh_token, expected_type=TokenType.REFRESH, settings=settings
        )
        user = await service.get_user_by_id(db, uuid.UUID(str(claims["sub"])))
    except (InvalidTokenError, KeyError, ValueError) as exc:
        raise credentials_error from exc

    if user is None or not user.is_active:
        raise credentials_error
    return _issue_token_pair(user=user, settings=settings)


@router.get("/me", response_model=UserRead, summary="Get the current user")
async def me(current_user: CurrentUserDep) -> User:
    return current_user
