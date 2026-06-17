# bikubenbarnepark.no

Static website plus a small local feedback service for FORENINGEN BIKUBEN BARNEPARK.

## Site Facts

- Domain: `https://bikubenbarnepark.no/`
- Organization: `FORENINGEN BIKUBEN BARNEPARK`
- Organization number: `934371275`
- Address: `Høybråtenveien 69, 1086 Oslo`
- Coordinates: `59.944292027157864, 10.924050830087147`

## Files

- `index.html`: main static page with SEO, Open Graph, Twitter card, event, and JSON-LD metadata.
- `innspill/index.html`: low-threshold feedback form that posts to `/api/feedback`.
- `innspill/takk/index.html`: thank-you page after a successful feedback submission.
- `personvern/index.html`: minimal privacy notice for feedback submissions.
- `feedback_service/`: FastAPI app, validation, and SQLite storage for feedback submissions.
- `scripts/export_feedback.py`: operator script for exporting feedback from SQLite as CSV or JSON.
- `index.md`: Markdown representation for agents. Traefik can serve this when `/` is requested with `Accept: text/markdown`.
- `styles.css`: site layout and accessibility styles.
- `robots.txt`: crawler policy and sitemap reference.
- `sitemap.xml`: sitemap for public pages.
- `llms.txt`: short machine-readable site summary for AI agents.
- `.well-known/api-catalog`: public description of the feedback endpoint.
- `.well-known/agent-skills/index.json`: empty agent skills index declaring that this site has no agent tools.
- `site.webmanifest`: basic web app metadata.
- `favicon.svg`: SVG favicon.
- `assets/source/`: original source images, kept unchanged.
- `assets/`: optimized derived images for page rendering and social sharing.
- `assets/video/`: optimized derived video and poster assets for page rendering.

## Feedback Service

The feedback form posts to a local FastAPI service. It stores submissions in SQLite and does not send email in v1.

Install and run locally:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export BIKUBEN_FEEDBACK_DB=/tmp/bikuben-feedback.sqlite3
export BIKUBEN_FEEDBACK_HASH_SALT=local-development-secret
export BIKUBEN_FORM_TOKEN_SECRET=local-development-token-secret
uvicorn feedback_service.app:app --host 127.0.0.1 --port 8095
```

Useful environment variables:

- `BIKUBEN_FEEDBACK_DB`: required absolute SQLite path. It must be outside the public static document root, for example `/var/lib/bikuben-feedback/feedback.sqlite3`.
- `BIKUBEN_FEEDBACK_HASH_SALT`: long random secret used when hashing remote addresses for anti-spam metadata.
- `BIKUBEN_FORM_TOKEN_SECRET`: long random secret used to sign form-load tokens. If omitted, the hash salt is used as fallback.
- `BIKUBEN_TRUST_PROXY_HEADERS`: set to `1` only when the service is reachable exclusively through a trusted reverse proxy that sets `X-Forwarded-For`.
- `BIKUBEN_MAX_REQUEST_BYTES`: maximum accepted request body size. Default: `32768`.

Export submissions:

```sh
python3 scripts/export_feedback.py --db /tmp/bikuben-feedback.sqlite3 --format csv --output feedback-exports/feedback.csv
python3 scripts/export_feedback.py --db /tmp/bikuben-feedback.sqlite3 --format json --output feedback-exports/feedback.json
```

The service should be routed by the edge/proxy so `GET /api/form-token` and `POST /api/feedback` reaches the FastAPI app while static files continue to be served normally. Configure the edge/proxy with a small request body limit for `/api/feedback`, for example tens of kilobytes rather than megabytes.

Container build for the feedback API:

```sh
docker build -t bikuben-feedback-api .
mkdir -p /tmp/bikuben-feedback
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -p 127.0.0.1:8095:8095 \
  -e BIKUBEN_FEEDBACK_DB=/var/lib/bikuben-feedback/feedback.sqlite3 \
  -e BIKUBEN_FEEDBACK_HASH_SALT=replace-with-secret \
  -e BIKUBEN_FORM_TOKEN_SECRET=replace-with-secret \
  -v /tmp/bikuben-feedback:/var/lib/bikuben-feedback \
  bikuben-feedback-api
```

The production container contract is documented in `SERVER_HANDOVER.md`. A minimal Compose fragment is available at `docs/feedback-compose.example.yml`.

The infrastructure deployment, persistence, routing, backup, monitoring, and rollback contract is documented in `docs/INFRA_HANDOVER.md`.

## Markdown for Agents

The repo includes `index.md` as a maintained Markdown version of the homepage.

Expected edge behavior:

- Browser/default requests for `/` should continue to serve `index.html` as `text/html`.
- Requests for `/` with `Accept: text/markdown` can be routed by Traefik to `index.md`.
- The Markdown response should use `Content-Type: text/markdown; charset=utf-8`.

## Image Workflow

Original images are kept unchanged. Derived image assets can be regenerated with ImageMagick and WebP tools if needed. Derived video assets can be regenerated with FFmpeg from local raw drone footage.

Current source images:

- `assets/source/park-drone-overview-source.jpeg`
- `assets/source/park-ground-overview-source.png`
- `assets/source/park-slide-source.png`
- `assets/source/park-stones-source.png`
- `assets/source/park-grill-source.png`
- `assets/source/park-playhouse-bench-source.png`

Current generated assets:

- `assets/park-overview-720.jpg`
- `assets/park-overview-720.webp`
- `assets/park-overview-1080.jpg`
- `assets/park-overview-1080.webp`
- `assets/park-overview-1440.jpg`
- `assets/park-overview-1440.webp`
- `assets/park-social-1200x630.jpg`
- `assets/park-social-1200x630.webp`
- `assets/park-slide-760.jpg`
- `assets/park-slide-760.webp`
- `assets/park-stones-760.jpg`
- `assets/park-stones-760.webp`
- `assets/park-grill-760.jpg`
- `assets/park-grill-760.webp`
- `assets/park-playhouse-bench-760.jpg`
- `assets/park-playhouse-bench-760.webp`
- `assets/video/park-overview-background.mp4`
- `assets/video/park-overview-background.webm`
- `assets/video/park-overview-poster.jpg`

## Checks

```sh
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -m py_compile feedback_service/app.py feedback_service/storage.py feedback_service/validation.py scripts/export_feedback.py
```
