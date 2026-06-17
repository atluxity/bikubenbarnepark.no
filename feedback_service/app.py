from __future__ import annotations

import os
from collections import defaultdict, deque
from time import time

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse

from .form_token import InvalidFormToken, TooFreshFormToken, create_form_token, validate_form_token
from .storage import insert_submission
from .validation import FeedbackValidationError, ProbableBotSubmission, validate_submission

app = FastAPI(title="Bikuben Barnepark feedback", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)

RATE_WINDOW_SECONDS = 15 * 60
RATE_LIMIT = 5
MAX_REQUEST_BYTES = int(os.environ.get("BIKUBEN_MAX_REQUEST_BYTES", "32768"))
TRUST_PROXY_HEADERS = os.environ.get("BIKUBEN_TRUST_PROXY_HEADERS", "").lower() in {"1", "true", "yes", "on"}
_recent_requests: dict[str, deque[float]] = defaultdict(deque)


def _remote_addr(request: Request) -> str:
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else ""


def _rate_limited(remote_addr: str) -> bool:
    now = time()
    bucket = _recent_requests[remote_addr]
    while bucket and now - bucket[0] > RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT:
        return True
    bucket.append(now)
    return False


def _request_too_large(request: Request) -> bool | None:
    content_length = request.headers.get("content-length")
    if not content_length:
        return False
    try:
        return int(content_length) > MAX_REQUEST_BYTES
    except ValueError:
        return None


@app.middleware("http")
async def reject_large_feedback_requests(request: Request, call_next):
    if request.url.path == "/api/feedback":
        too_large = _request_too_large(request)
        if too_large is None:
            return PlainTextResponse("Ugyldig forespørsel.", status_code=400)
        if too_large:
            return PlainTextResponse("Innsendingen er for stor.", status_code=413)
    return await call_next(request)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/form-token")
def form_token() -> JSONResponse:
    return JSONResponse(
        {"token": create_form_token()},
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/feedback")
async def submit_feedback(
    request: Request,
    topic: str = Form(...),
    message: str = Form(...),
    name: str = Form(""),
    contact: str = Form(""),
    help_text: str = Form(""),
    consent: str = Form(""),
    website: str = Form(""),
    form_token: str = Form(""),
) -> Response:
    remote_addr = _remote_addr(request)
    if _rate_limited(remote_addr):
        return PlainTextResponse("For mange innsendinger på kort tid.", status_code=429)

    try:
        validate_form_token(form_token)
        submission = validate_submission(
            topic=topic,
            message=message,
            name=name,
            contact=contact,
            help_text=help_text,
            consent=consent,
            honeypot=website,
        )
    except (InvalidFormToken, TooFreshFormToken, ProbableBotSubmission):
        return RedirectResponse(url="/innspill/takk/", status_code=303)
    except FeedbackValidationError as exc:
        return PlainTextResponse("Innsendingen kunne ikke lagres: " + " ".join(exc.errors), status_code=400)

    insert_submission(
        submission,
        remote_addr=remote_addr,
        user_agent=request.headers.get("user-agent", ""),
    )
    return RedirectResponse(url="/innspill/takk/", status_code=303)
