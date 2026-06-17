# Server Handover: Bikuben Website and Feedback Runtime

This repository contains the public static website for `bikubenbarnepark.no` plus a small private feedback API used by the `/innspill/` form. The server automation should treat this as two different surfaces:

- Public static files served to ordinary web visitors.
- Private backend runtime and SQLite storage used only behind the reverse proxy.

The feedback feature intentionally has a low-threshold user experience, but all submitted data is untrusted internet input and must be handled as personal data.

The infrastructure-specific deployment handover is maintained in `docs/INFRA_HANDOVER.md`.

## Public Surface

Expected public domain:

```text
https://bikubenbarnepark.no/
```

Expected public pages and static metadata:

- `/`
- `/innspill/`
- `/innspill/takk/`
- `/personvern/`
- `/robots.txt`
- `/sitemap.xml`
- `/llms.txt`
- `/.well-known/api-catalog`
- `/.well-known/agent-skills/index.json`
- `/assets/*`
- `/assets/video/*`
- `/styles.css`
- `/favicon.svg`
- `/site.webmanifest`

These files are public by design. They may be served directly by the web server or reverse proxy from the deployed website directory.

## Private Surface

The feedback API must run as a private local service. It should not listen on a public interface and should not be directly reachable from the internet.

Expected application:

```text
feedback_service.app:app
```

Expected local bind shape:

```text
127.0.0.1:8095
```

Expected public routes proxied to the private API:

```text
GET  /api/health
GET  /api/form-token
POST /api/feedback
```

Expected proxy routing:

```text
/api/*       -> http://127.0.0.1:8095/api/*
everything else -> static website files
```

Do not expose FastAPI docs, OpenAPI JSON, debug middleware, Python tracebacks, or the ASGI server directly. The application disables FastAPI docs and OpenAPI routes; the server should preserve that posture.

## Container Contract

The site repository provides a production container contract for the private feedback API.

Container build:

```sh
docker build -t bikuben-feedback-api .
```

Default container command:

```text
uvicorn feedback_service.app:app --host 0.0.0.0 --port 8095
```

Important distinction:

- `0.0.0.0` is correct inside the container so the service is reachable on the container network.
- The container port must not be published directly to the public internet.
- The public edge should route only `/api/*` to this service through the private Compose/container network.

Image expectations:

- Installs Python dependencies from `requirements.txt`.
- Runs the FastAPI app on port `8095`.
- Includes `feedback_service/` and `scripts/export_feedback.py`.
- Does not bake secrets, SQLite databases, exports, virtualenvs, logs, or runtime state into the image.
- Writes logs to stdout/stderr through the ASGI server/container runtime.
- Has a container healthcheck against `GET /api/health`.

Runtime expectations:

- Provide all required environment variables at runtime.
- Bind-mount or otherwise provide the private persistent data directory containing the SQLite database.
- Ensure the mounted database directory is writable by container UID/GID `10001:10001`.
- Keep the mounted database directory outside the static web root.

Minimal production-ish Compose fragment:

```yaml
services:
  feedback:
    build:
      context: /home/atluxity/git/bikubenbarnepark.no
      dockerfile: Dockerfile
    environment:
      BIKUBEN_FEEDBACK_DB: /var/lib/bikuben-feedback/feedback.sqlite3
      BIKUBEN_TRUST_PROXY_HEADERS: "1"
      BIKUBEN_MAX_REQUEST_BYTES: "32768"
    env_file:
      - /opt/bikubenbarnepark-site/secrets/feedback.env
    volumes:
      - /var/lib/bikuben-feedback:/var/lib/bikuben-feedback
    expose:
      - "8095"
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:8095/api/health', timeout=3)); raise SystemExit(0 if data.get('status') == 'ok' else 1)"
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

A standalone copy of this example is also kept at `docs/feedback-compose.example.yml`.

The infra repository should still own Traefik, TLS, nginx/static serving, production secret storage, persistent host paths, file permissions, backups, monitoring, and public health probing.

## Required Secrets and Configuration

Required environment variables for production:

- `BIKUBEN_FEEDBACK_DB`: absolute SQLite database path outside the public static document root.
- `BIKUBEN_FEEDBACK_HASH_SALT`: long random secret used to HMAC-hash remote addresses before storage.
- `BIKUBEN_FORM_TOKEN_SECRET`: long random secret used to sign form-load tokens.

Optional environment variables:

- `BIKUBEN_TRUST_PROXY_HEADERS`: set to `1` only when the API is reachable exclusively through a trusted reverse proxy that sets `X-Forwarded-For`.
- `BIKUBEN_MAX_REQUEST_BYTES`: maximum accepted body size for `/api/feedback`; default is `32768`.

Secrets must not be committed to this repository, rendered in static files, exposed in logs, included in exported feedback files, or made available to browser-side JavaScript.

`BIKUBEN_FEEDBACK_DB` must point outside the website checkout/deploy directory. The application fails closed if this value is missing.

Good path shape:

```text
/var/lib/bikuben-feedback/feedback.sqlite3
```

Bad path shapes:

```text
/srv/bikubenbarnepark.no/feedback.sqlite3
/srv/bikubenbarnepark.no/feedback-data/feedback.sqlite3
/home/.../git/bikubenbarnepark.no/feedback.sqlite3
```

## Filesystem Expectations

Public website directory:

- Contains the deployed static files from this repository.
- Is readable by the web server.
- Must not contain runtime SQLite databases, feedback exports, secrets, virtualenv credentials, or server-local config.

Private runtime data directory:

- Owned by the feedback service user.
- Not inside the public website directory.
- Writable by the feedback service.
- Backed up if feedback submissions should survive host replacement.
- Not served by the web server under any alias.

Suggested private runtime data path:

```text
/var/lib/bikuben-feedback/
```

Suggested service log posture:

- Log service start, stop, health, and errors.
- Do not log full feedback messages, contact fields, request bodies, form tokens, or secrets.
- Keep logs readable only by operators who are allowed to see operational data.

## What Must Not Be Publicly Accessible

The following must not be retrievable by a web visitor:

- SQLite database files.
- Feedback export files.
- Environment files containing secrets.
- Python virtualenv internals.
- `__pycache__/`.
- Raw server logs.
- Any path under the private runtime data directory.
- Any future admin interface unless it has real authentication and authorization.

Defense-in-depth proxy denies are recommended even though the database must live outside the document root:

```text
*.sqlite
*.sqlite3
*.db
/feedback-data/*
/feedback-exports/*
/.env
/.venv/*
```

Do not rely on `.gitignore` as a security boundary. It only prevents accidental commits.

## Expected Feedback Traffic

Normal browser flow:

1. Visitor loads `/innspill/`.
2. Browser requests `GET /api/form-token`.
3. API returns JSON containing a signed form token with `Cache-Control: no-store`.
4. Visitor fills the form.
5. Browser submits `POST /api/feedback` as form data.
6. API validates the token and fields.
7. API stores accepted feedback in SQLite.
8. API redirects to `/innspill/takk/` with HTTP 303.

Expected content types:

- `/api/form-token`: JSON response.
- `/api/feedback`: browser form submission, normally `application/x-www-form-urlencoded` or `multipart/form-data`.

Expected traffic volume is low. This is not designed as a high-throughput service. Server automation should still run it under a supervisor that restarts it after reboot or crash.

## Expected API Behavior

`GET /api/health`

- Returns HTTP 200 and JSON status when the service is running.
- Intended for local and external health checks.

`GET /api/form-token`

- Returns HTTP 200 JSON with a `token` field.
- Must not be cached by browsers, proxies, or CDNs.
- Token signing uses `BIKUBEN_FORM_TOKEN_SECRET`.

`POST /api/feedback`

- Accepts `topic` and `message`.
- Accepts optional `name`, `contact`, and `help_text`.
- Requires `consent` when name, contact, or help text is provided.
- Redirects accepted submissions to `/innspill/takk/`.
- Returns HTTP 400 for normal user-correctable validation errors.
- Returns HTTP 413 if the request body is too large.
- Returns HTTP 429 for too many submissions from the same remote address.

Anti-bot behavior that must look normal:

- Missing, invalid, expired, or too-fresh form token redirects to `/innspill/takk/` but does not store.
- Honeypot field `website` containing data redirects to `/innspill/takk/` but does not store.
- A token submitted within 3 seconds of being issued is treated as bot-like and is not stored.

This is intentional. Do not change these cases into visible errors unless the product decision changes, because visible errors help bots tune their submissions.

## Input Handling and Security Expectations

All submitted fields are untrusted.

Current backend controls:

- Pydantic validation with `extra="forbid"` for the submission model.
- Topic allowlist.
- Required message length validation.
- Maximum field lengths.
- Control-character cleanup and whitespace normalization.
- Consent enforcement when optional identifying/help fields are present.
- Honeypot field.
- Server-signed form-load token.
- Minimum 3 second delay between token issuance and accepted submission.
- Token expiry after 4 hours.
- HMAC comparison for token signatures.
- Parameterized SQLite inserts and selects.
- No shell commands are built from submitted input.
- No email is sent in this version.
- CSV export prefixes formula-like cells to reduce spreadsheet formula injection risk.
- FastAPI docs and OpenAPI routes are disabled.

Infrastructure controls still expected:

- TLS termination for the public site.
- Private-only API bind address.
- Reverse proxy request body limit for `/api/feedback`, preferably matching or below the app limit.
- Reasonable connection/request timeout settings.
- Basic access logging without request bodies.
- OS/package dependency updates.
- Recurring Python dependency vulnerability checks.
- File permissions that prevent the web server from reading private data unless it is also the service user and explicitly needs that access.

Do not add future functionality that renders stored feedback as HTML without escaping. Future admin views should treat stored messages as untrusted text, not as safe markup.

## Stored Data

The SQLite database stores:

- Submission timestamp.
- Topic.
- Message.
- Optional help text.
- Optional name.
- Optional contact detail.
- Consent flag.
- Salted remote-address hash.
- User agent.

The database can contain personal data. It should be protected accordingly.

Expected privacy posture:

- Anonymous feedback is allowed.
- Contact details are optional.
- Contact details are used only for possible follow-up.
- Retention policy currently stated on the site is generally up to 12 months unless follow-up is active or deletion is requested.
- Exports are personal-data artifacts and must be handled with the same care as the database.

## Export Expectations

Operator export script:

```sh
python3 scripts/export_feedback.py \
  --db /var/lib/bikuben-feedback/feedback.sqlite3 \
  --format csv \
  --output /secure/operator/path/feedback.csv
```

JSON export is also supported:

```sh
python3 scripts/export_feedback.py \
  --db /var/lib/bikuben-feedback/feedback.sqlite3 \
  --format json \
  --output /secure/operator/path/feedback.json
```

Export files must not be written under the public website directory. If temporary exports are needed, write them to an operator-only path and delete them after use.

## Deployment Expectations

The automation should provide:

- Static file deployment for the website.
- Python virtual environment or equivalent isolated runtime for the feedback service.
- Installation from `requirements.txt`.
- Private service user.
- Persistent private SQLite directory.
- Production secrets via environment or equivalent secret management.
- Supervisor/system service that starts on boot and restarts on failure.
- Reverse proxy routing for `/api/*`.
- TLS for the public site.
- Request body limits for `/api/feedback`.
- Log rotation.
- Backup decision for the SQLite database.
- A documented way for an operator to export feedback.

The automation should not:

- Put the SQLite database inside the git checkout or public static root.
- Put feedback exports inside the public static root.
- Commit generated databases, exports, virtualenvs, logs, or Python cache directories.
- Expose the feedback service on `0.0.0.0`.
- Trust `X-Forwarded-For` unless direct access to the API port is impossible from the internet.
- Add browser-side-only security checks and treat them as enforcement.

## Verification After Deployment

Health check:

```sh
curl -i https://bikubenbarnepark.no/api/health
```

Expected:

```text
HTTP 200
{"status":"ok"}
```

Form-token check:

```sh
curl -i https://bikubenbarnepark.no/api/form-token
```

Expected:

- HTTP 200.
- JSON response with a `token` field.
- `Cache-Control: no-store`.

Anonymous submission check:

```sh
TOKEN="$(curl -s https://bikubenbarnepark.no/api/form-token | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
sleep 4
curl -i -X POST https://bikubenbarnepark.no/api/feedback \
  -F topic=ide \
  -F message="Testinnspill fra serveroppsett" \
  -F form_token="$TOKEN"
```

Expected:

```text
HTTP 303
Location: /innspill/takk/
```

Consent validation check:

```sh
TOKEN="$(curl -s https://bikubenbarnepark.no/api/form-token | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
sleep 4
curl -i -X POST https://bikubenbarnepark.no/api/feedback \
  -F topic=bidra \
  -F message="Jeg kan hjelpe" \
  -F contact="test@example.com" \
  -F form_token="$TOKEN"
```

Expected:

```text
HTTP 400
```

Accepted contact submission check:

```sh
TOKEN="$(curl -s https://bikubenbarnepark.no/api/form-token | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
sleep 4
curl -i -X POST https://bikubenbarnepark.no/api/feedback \
  -F topic=bidra \
  -F message="Jeg kan hjelpe" \
  -F contact="test@example.com" \
  -F consent=yes \
  -F form_token="$TOKEN"
```

Expected:

```text
HTTP 303
Location: /innspill/takk/
```

Bot-like fast submission check:

```sh
TOKEN="$(curl -s https://bikubenbarnepark.no/api/form-token | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
curl -i -X POST https://bikubenbarnepark.no/api/feedback \
  -F topic=ide \
  -F message="For rask innsending" \
  -F form_token="$TOKEN"
```

Expected:

```text
HTTP 303
Location: /innspill/takk/
```

Also expected:

- The fast submission is not stored.
- The accepted submissions are stored.
- No SQLite database or export file is retrievable over HTTPS.

Private file exposure checks should return 404 or another non-success status:

```sh
curl -i https://bikubenbarnepark.no/feedback.sqlite3
curl -i https://bikubenbarnepark.no/feedback-data/feedback.sqlite3
curl -i https://bikubenbarnepark.no/feedback-exports/feedback.csv
curl -i https://bikubenbarnepark.no/.env
```

## Local Repository Checks Before Deployment

Useful checks:

```sh
.venv/bin/python -m py_compile feedback_service/app.py feedback_service/storage.py feedback_service/validation.py feedback_service/form_token.py scripts/export_feedback.py
.venv/bin/python -m unittest discover -s tests
git diff --check
```

Runtime artifacts that should not be committed:

- `.venv/`
- `feedback-data/`
- `feedback-exports/`
- SQLite database files.
- Python `__pycache__/`.
- Logs.
- Environment files containing secrets.
