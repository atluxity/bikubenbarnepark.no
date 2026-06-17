# Infrastructure Handover: bikubenbarnepark.no

This document describes what the infrastructure configuration must provide for `bikubenbarnepark.no`.

The site repository owns:

- Public static website files.
- Feedback API application code.
- Python dependency definitions.
- Production `Dockerfile`.
- Container command, port, and healthcheck.
- SQLite schema and export tooling.

The infrastructure repository owns:

- Deployment and update policy.
- Container orchestration and private networking.
- nginx, Traefik, DNS, and TLS.
- Production secrets.
- Persistent storage and permissions.
- Backups, monitoring, logging, and rollback.

The application-level details are documented in `SERVER_HANDOVER.md`. This document is the expected infrastructure contract.

## Required Architecture

The deployed site has two services:

1. A static web service serving the public files from this repository.
2. A private feedback API container built from this repository's `Dockerfile`.

Expected request routing:

```text
Internet
  -> Traefik/TLS
  -> nginx
       /api/*  -> feedback:8095
       all other paths -> static website files
```

The feedback container must not publish port `8095` on the host or expose it directly to the internet. It should only be reachable from nginx over a private Compose network.

## Site Repository Deployment

The infrastructure should deploy a known revision of:

```text
/home/atluxity/git/bikubenbarnepark.no
```

The update process may use a checkout, release directory, or image build pipeline, but it must provide:

- A deterministic source revision.
- A successful container build before switching production traffic.
- A way to roll back to the previous source revision or image.
- Persistent feedback data that is independent of source checkout and image lifecycle.

Do not store runtime databases, exports, secrets, or logs in the site checkout.

## Feedback Image Contract

Build context:

```text
/home/atluxity/git/bikubenbarnepark.no
```

Dockerfile:

```text
Dockerfile
```

Container command:

```text
uvicorn feedback_service.app:app --host 0.0.0.0 --port 8095
```

Container port:

```text
8095/tcp
```

Health endpoint:

```text
GET /api/health
```

Healthy response:

```json
{"status":"ok"}
```

Container runtime user:

```text
UID 10001
GID 10001
```

The image includes a Docker healthcheck. Compose or other orchestration may repeat or override it if needed.

## Compose Shape

The precise production Compose file belongs to infra. It should be equivalent to:

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
    restart: unless-stopped
```

nginx and `feedback` must share a private container network. There should be no `ports:` mapping for the feedback service.

## Production Secrets

Required secrets:

```text
BIKUBEN_FEEDBACK_HASH_SALT
BIKUBEN_FORM_TOKEN_SECRET
```

Required non-secret configuration:

```text
BIKUBEN_FEEDBACK_DB=/var/lib/bikuben-feedback/feedback.sqlite3
```

Optional configuration:

```text
BIKUBEN_TRUST_PROXY_HEADERS=1
BIKUBEN_MAX_REQUEST_BYTES=32768
```

Secret requirements:

- Generate independent, cryptographically random values.
- Store them in Ansible Vault or equivalent secret management.
- Render them only into a root/operator-controlled runtime environment file.
- Do not store them in Git, Compose YAML, static files, container images, or logs.
- Do not expose them to browser JavaScript.

Suggested runtime file:

```text
/opt/bikubenbarnepark-site/secrets/feedback.env
```

Suggested permissions:

```text
owner: root
group: root or the deployment service group
mode: 0600 or equivalently restrictive
```

Secret rotation effects:

- Rotating `BIKUBEN_FORM_TOKEN_SECRET` immediately invalidates outstanding form tokens. This is safe; visitors can reload the form.
- Rotating `BIKUBEN_FEEDBACK_HASH_SALT` changes future remote-address hashes, so historical and new hashes will no longer correlate. This is acceptable but should be intentional.
- Restart the feedback container after changing environment values.

Production must provide both secrets. The application's local-development fallback values are not suitable for production.

## Persistent Storage

Expected host directory:

```text
/var/lib/bikuben-feedback
```

Expected database:

```text
/var/lib/bikuben-feedback/feedback.sqlite3
```

The host directory must:

- Exist before container startup.
- Be owned by or writable by UID/GID `10001:10001`.
- Not be under the static document root.
- Not be mounted into nginx.
- Not be reachable through any web-server alias.
- Survive container recreation, image rollback, and source checkout replacement.

Suggested ownership and mode:

```text
owner: 10001
group: 10001
mode: 0700
```

SQLite uses WAL mode. Runtime files may include:

```text
feedback.sqlite3
feedback.sqlite3-wal
feedback.sqlite3-shm
```

These are all private runtime data.

## Backup Expectations

The infra owner must decide whether feedback submissions require backup. If enabled, the backup must be SQLite-aware.

Do not assume that copying only `feedback.sqlite3` while the service is running produces a complete backup, because committed data may still be in the WAL file.

Use one of these approaches:

- Use SQLite's online backup mechanism.
- Run an explicit WAL checkpoint and take a coordinated backup.
- Stop the feedback container briefly and copy the complete database state.
- Use a backup tool that explicitly supports live SQLite/WAL databases.

Backup requirements:

- Store backups outside the public web root.
- Apply the same confidentiality controls as the live database.
- Define retention consistent with the site's stated personal-data retention.
- Test restoration, not only backup creation.
- Ensure restore preserves or repairs ownership for UID/GID `10001:10001`.

## nginx Requirements

nginx should:

- Serve static site files for all normal public paths.
- Proxy only `/api/*` to `http://feedback:8095`.
- Preserve the request method and form body.
- Set standard forwarding headers.
- Apply a small request-body limit to `/api/feedback`.
- Use reasonable request and upstream timeouts.
- Avoid logging request bodies.
- Return a controlled gateway error if the feedback service is unavailable.

The application expects the original client address through `X-Forwarded-For` when:

```text
BIKUBEN_TRUST_PROXY_HEADERS=1
```

Only enable this setting when the feedback container cannot be reached directly by untrusted clients. nginx should replace or correctly append forwarding headers so arbitrary client-supplied values are not trusted as authoritative.

Recommended request body limit:

```text
32 KiB
```

The application also enforces `BIKUBEN_MAX_REQUEST_BYTES`, but nginx should reject oversized requests before forwarding them.

Do not cache:

```text
/api/form-token
/api/feedback
```

The form-token response already includes `Cache-Control: no-store`; proxy/CDN configuration must respect it.

## Traefik and TLS

Traefik remains responsible for:

- Public host routing for `bikubenbarnepark.no`.
- HTTPS certificates and renewal.
- HTTP-to-HTTPS redirect policy.
- Forwarding public traffic to nginx.

Traefik should not route directly to the feedback API. nginx remains the application split point between static content and `/api/*`.

## Public and Private Paths

Expected public API routes:

```text
GET  /api/health
GET  /api/form-token
POST /api/feedback
```

No other application API route is required.

The following must not be publicly retrievable:

- `/var/lib/bikuben-feedback/*`
- SQLite database, WAL, or shared-memory files.
- Feedback exports.
- Secret environment files.
- Container runtime configuration containing secrets.
- `.env` files.
- `.venv/`.
- Python cache files.
- Server logs.

Defense-in-depth nginx denies are recommended for:

```text
*.sqlite
*.sqlite3
*.sqlite3-wal
*.sqlite3-shm
*.db
/.env
/.venv/*
/feedback-data/*
/feedback-exports/*
```

The primary security boundary remains keeping all private files outside the static document root.

## Expected Traffic and Responses

Normal user flow:

1. Browser loads `/innspill/`.
2. Browser requests `GET /api/form-token`.
3. Browser waits while the visitor fills the form.
4. Browser posts form data to `POST /api/feedback`.
5. API redirects to `/innspill/takk/`.

Expected status behavior:

- Health check: HTTP 200.
- Token request: HTTP 200 with `Cache-Control: no-store`.
- Valid feedback: HTTP 303 to `/innspill/takk/`.
- Normal validation failure: HTTP 400.
- Oversized request: HTTP 413.
- Rate limit: HTTP 429.
- Bot-like submission: HTTP 303 to `/innspill/takk/`, but no database row.

Bot-like submissions intentionally look successful. Infra tests must verify database state, not only HTTP status, when testing missing, invalid, or too-fresh form tokens.

Expected traffic volume is low. A single API container is sufficient. The current in-memory rate limiter is process-local, so do not horizontally scale the API without revisiting rate-limit behavior and SQLite write coordination.

## Logging

Container logs should go to stdout/stderr and be collected by the existing container logging mechanism.

Allowed operational logging:

- Container startup and shutdown.
- Health and availability failures.
- HTTP method, route, status, response time, and limited network metadata.
- Application exceptions without request bodies.

Do not log:

- Feedback messages.
- Names or contact fields.
- Form bodies.
- Form tokens.
- Secrets.
- Database contents.

Configure log rotation or retention limits so container logs cannot consume unbounded disk space.

## Monitoring

Monitor at least:

- Container running state.
- Docker health status.
- Public `GET https://bikubenbarnepark.no/api/health`.
- nginx upstream failures for the feedback service.
- Persistent filesystem free space.
- Backup success and restore-test status if backups are enabled.
- TLS certificate validity through existing site monitoring.

An HTTP 200 from `/api/health` proves the process is serving requests. It does not currently perform a database write/read check. Deployment verification must separately confirm database writability.

## Deployment Sequence

Recommended sequence:

1. Deploy or update the site repository to a known revision.
2. Build the feedback image.
3. Provision secrets.
4. Create `/var/lib/bikuben-feedback` with ownership `10001:10001`.
5. Start or recreate the feedback container.
6. Wait for the container healthcheck to pass.
7. Verify the private API from nginx or the Compose network.
8. Apply/reload nginx routing.
9. Verify the public health and form-token endpoints.
10. Run an accepted submission smoke test.
11. Confirm the row exists in SQLite.
12. Run a bot-like fast submission test.
13. Confirm the bot-like submission does not create a row.
14. Confirm private-file probe URLs return a non-success status.

Avoid destroying or recreating the persistent host data directory during deployment.

## Rollback

Application rollback:

- Deploy the previous source revision or image.
- Keep `/var/lib/bikuben-feedback` mounted unchanged.
- Reuse the same production secrets unless rotation is intentional.
- Verify the previous image can read the existing SQLite schema before switching traffic.

Infrastructure rollback:

- Restore the previous Compose/nginx configuration.
- Do not roll back the database file merely because application code is rolled back.
- Restore a database backup only for actual data corruption or explicit data-recovery needs.

The current application creates its table if missing and does not have a separate migration framework. Future schema changes must add a documented forward/backward compatibility and migration plan before deployment.

## Operator Export

CSV export contract:

```sh
python3 scripts/export_feedback.py \
  --db /var/lib/bikuben-feedback/feedback.sqlite3 \
  --format csv \
  --output /secure/operator/path/feedback.csv
```

JSON export is also supported.

When executing inside the container, the output path must be a mounted operator-only destination. Alternatively, execute the script from a trusted checkout with read access to the database.

Exports:

- Contain personal data.
- Must never be written under the static web root.
- Must be readable only by authorized operators.
- Should be deleted when no longer needed.
- Must not be attached to public tickets or copied into Git.

## Acceptance Tests

Build:

```sh
docker build -t bikuben-feedback-api /home/atluxity/git/bikubenbarnepark.no
```

Health:

```sh
curl -fsS https://bikubenbarnepark.no/api/health
```

Expected:

```json
{"status":"ok"}
```

Token:

```sh
curl -i https://bikubenbarnepark.no/api/form-token
```

Expected:

- HTTP 200.
- JSON `token`.
- `Cache-Control: no-store`.

Accepted submission:

```sh
TOKEN="$(curl -fsS https://bikubenbarnepark.no/api/form-token \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
sleep 4
curl -i -X POST https://bikubenbarnepark.no/api/feedback \
  -F topic=ide \
  -F message="Infrastructure deployment test" \
  -F form_token="$TOKEN"
```

Expected:

```text
HTTP 303
Location: /innspill/takk/
```

Then verify that exactly one corresponding row exists in the database.

Fast bot-like submission:

```sh
TOKEN="$(curl -fsS https://bikubenbarnepark.no/api/form-token \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')"
curl -i -X POST https://bikubenbarnepark.no/api/feedback \
  -F topic=ide \
  -F message="Fast infrastructure test" \
  -F form_token="$TOKEN"
```

Expected:

- HTTP 303 to `/innspill/takk/`.
- No corresponding database row.

Private-file probes:

```sh
curl -i https://bikubenbarnepark.no/feedback.sqlite3
curl -i https://bikubenbarnepark.no/feedback.sqlite3-wal
curl -i https://bikubenbarnepark.no/feedback-data/feedback.sqlite3
curl -i https://bikubenbarnepark.no/feedback-exports/feedback.csv
curl -i https://bikubenbarnepark.no/.env
```

All must return a non-success response and no private file content.

## Infra Completion Criteria

Infrastructure integration is complete when:

- Static pages continue to load normally.
- `/api/*` is proxied only to the private feedback container.
- The feedback container is not host-published.
- Required secrets are supplied through protected runtime configuration.
- The database directory exists outside the web root with ownership `10001:10001`.
- The container is healthy.
- A valid delayed submission is persisted.
- A too-fast submission appears successful but is not persisted.
- Oversized requests are rejected at nginx.
- SQLite and secret paths are not publicly accessible.
- Logging does not capture submitted form data.
- Backup and retention decisions are documented.
- Rollback leaves persistent feedback data intact.
