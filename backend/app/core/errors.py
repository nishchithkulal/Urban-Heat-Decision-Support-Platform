"""Centralized error handling.

One exception handler, one error shape, applied to every route. API consumers never see
a stack trace, an internal file path, or any other implementation detail (CLAUDE.md
section 19). The shape follows RFC 9457 (``application/problem+json``) so it is a
documented standard rather than a bespoke convention the frontend has to be told about
separately.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"

_DEFAULT_TITLES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "Bad Request",
    status.HTTP_401_UNAUTHORIZED: "Unauthorized",
    status.HTTP_403_FORBIDDEN: "Forbidden",
    status.HTTP_404_NOT_FOUND: "Not Found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Method Not Allowed",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "Unprocessable Entity",
    status.HTTP_429_TOO_MANY_REQUESTS: "Too Many Requests",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal Server Error",
}


def _problem_response(
    *,
    status_code: int,
    detail: str,
    request: Request,
    errors: list[dict[str, object]] | None = None,
) -> JSONResponse:
    body: dict[str, object] = {
        "type": "about:blank",
        "title": _DEFAULT_TITLES.get(status_code, "Error"),
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
    }
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(status_code=status_code, content=body, media_type=PROBLEM_JSON)


async def _handle_http_exception(request: Request, exc: Exception) -> JSONResponse:
    # Starlette's add_exception_handler is registered by exception class, which
    # guarantees exc's runtime type here, but its typeshed signature is contravariant
    # on Exception — hence the broad parameter type and the assert to recover the
    # narrow one for mypy.
    assert isinstance(exc, StarletteHTTPException)
    return _problem_response(
        status_code=exc.status_code,
        detail=str(exc.detail),
        request=request,
    )


async def _handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    # Field-level messages only. Pydantic error dicts can include the offending input
    # value, which may contain sensitive data the client just submitted (a password
    # field failing validation, for instance) — that is not safe to echo back.
    errors = [
        {"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]}
        for error in exc.errors()
    ]
    return _problem_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Request validation failed.",
        request=request,
        errors=errors,
    )


async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    # The only place an unhandled exception is allowed to reach a log line with its
    # full detail. Everywhere downstream of here sees the generic message below.
    logger.exception("Unhandled exception while processing request", exc_info=exc)
    return _problem_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred.",
        request=request,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)
    app.add_exception_handler(HTTPException, _handle_http_exception)
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(Exception, _handle_unexpected_error)
