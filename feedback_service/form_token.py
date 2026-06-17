from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import time

MIN_FORM_SECONDS = 3.0
MAX_FORM_SECONDS = 4 * 60 * 60
TOKEN_SECRET = os.environ.get(
    "BIKUBEN_FORM_TOKEN_SECRET",
    os.environ.get("BIKUBEN_FEEDBACK_HASH_SALT", "local-development-token-secret"),
)


class InvalidFormToken(ValueError):
    pass


class TooFreshFormToken(ValueError):
    pass


def _sign(payload: str) -> str:
    digest = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def create_form_token(now: float | None = None) -> str:
    issued_ms = int((now or time.time()) * 1000)
    nonce = secrets.token_urlsafe(16)
    payload = f"{issued_ms}.{nonce}"
    return f"{payload}.{_sign(payload)}"


def validate_form_token(token: str | None, now: float | None = None) -> None:
    if not token:
        raise InvalidFormToken()
    try:
        issued_ms_text, nonce, signature = token.split(".", 2)
        issued_ms = int(issued_ms_text)
    except (ValueError, AttributeError):
        raise InvalidFormToken() from None

    payload = f"{issued_ms_text}.{nonce}"
    if not hmac.compare_digest(signature, _sign(payload)):
        raise InvalidFormToken()

    age_seconds = ((now or time.time()) * 1000 - issued_ms) / 1000
    if age_seconds <= MIN_FORM_SECONDS:
        raise TooFreshFormToken()
    if age_seconds > MAX_FORM_SECONDS or age_seconds < 0:
        raise InvalidFormToken()
