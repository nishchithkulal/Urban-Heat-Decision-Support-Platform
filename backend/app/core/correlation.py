"""Request correlation IDs.

Every log line emitted while handling a request carries the same identifier. That is
what makes logs reassemblable into a single request story once the system spans more
than one process, and it is why this lands in Phase 1 rather than with the observability
work: retrofitting correlation into an existing codebase means revisiting every log call
site (CLAUDE.md section 18).

The identifier lives in a :class:`contextvars.ContextVar` so it propagates through
``async`` call chains automatically, without threading a request object through every
function signature.
"""

from __future__ import annotations

import re
import uuid
from contextvars import ContextVar

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

CORRELATION_ID_HEADER = "X-Request-ID"

# A correlation ID may arrive from an untrusted client and is written into logs, so it
# is constrained to a short, safe alphabet. Unbounded client-controlled data in a log
# stream is a log-injection vector and a denial-of-service vector against log storage
# (CLAUDE.md section 20: never trust client-provided input).
_MAX_LENGTH = 128
_SAFE_PATTERN = re.compile(r"[A-Za-z0-9._:\-]+")

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def new_correlation_id() -> str:
    return uuid.uuid4().hex


def get_correlation_id() -> str | None:
    """Return the current request's correlation ID, if any."""
    return _correlation_id.get()


def _clean(value: str | None) -> str | None:
    """Accept a client-supplied ID only if it is short and safely formed."""
    if value is None:
        return None
    candidate = value.strip()
    if not candidate or len(candidate) > _MAX_LENGTH:
        return None
    if not _SAFE_PATTERN.fullmatch(candidate):
        return None
    return candidate


class CorrelationIdMiddleware:
    """Assign a correlation ID to every HTTP request and echo it on the response.

    Written as raw ASGI rather than as a ``BaseHTTPMiddleware`` subclass. Starlette's
    ``BaseHTTPMiddleware`` runs the downstream application in a separate task, which
    complicates context propagation and interferes with streaming responses and
    background tasks. Raw ASGI avoids that class of problem for about the same amount
    of code.
    """

    def __init__(self, app: ASGIApp, header_name: str = CORRELATION_ID_HEADER) -> None:
        self.app = app
        self.header_name = header_name

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = Headers(scope=scope).get(self.header_name)
        correlation_id = _clean(incoming) or new_correlation_id()
        token = _correlation_id.set(correlation_id)

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                MutableHeaders(raw=message["headers"]).append(
                    self.header_name, correlation_id
                )
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            _correlation_id.reset(token)
