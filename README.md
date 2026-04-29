# bikubenbarnepark.no

Static website for FORENINGEN BIKUBEN BARNEPARK.

## Site Facts

- Domain: `https://bikubenbarnepark.no/`
- Organization: `FORENINGEN BIKUBEN BARNEPARK`
- Organization number: `934371275`
- Address: `Høybråtenveien 69, 1086 Oslo`
- Coordinates: `59.944292027157864, 10.924050830087147`

## Files

- `index.html`: main static page with SEO, Open Graph, Twitter card, and JSON-LD metadata.
- `index.md`: Markdown representation for agents. Traefik can serve this when `/` is requested with `Accept: text/markdown`.
- `styles.css`: site layout and accessibility styles.
- `robots.txt`: crawler policy and sitemap reference.
- `sitemap.xml`: sitemap for the root page.
- `llms.txt`: short machine-readable site summary for AI agents.
- `.well-known/api-catalog`: empty API catalog declaring that this static site has no public API.
- `.well-known/agent-skills/index.json`: empty agent skills index declaring that this static site has no agent tools.
- `site.webmanifest`: basic web app metadata.
- `favicon.svg`: SVG favicon.
- `assets/source/`: original source images, kept unchanged.
- `assets/`: optimized derived images for page rendering and social sharing.

## Markdown for Agents

The repo includes `index.md` as a maintained Markdown version of the homepage.

Expected edge behavior:

- Browser/default requests for `/` should continue to serve `index.html` as `text/html`.
- Requests for `/` with `Accept: text/markdown` can be routed by Traefik to `index.md`.
- The Markdown response should use `Content-Type: text/markdown; charset=utf-8`.

## Image Workflow

Original images are kept unchanged. Derived assets can be regenerated with ImageMagick and WebP tools if needed.

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
