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
- `oversikt1.png`, `sklie.png`, `steiner.png`, `grill.png`, `hytte-benk.png`: source images.
- `assets/`: optimized derived images for page rendering and social sharing.

## Markdown for Agents

The repo includes `index.md` as a maintained Markdown version of the homepage.

Expected edge behavior:

- Browser/default requests for `/` should continue to serve `index.html` as `text/html`.
- Requests for `/` with `Accept: text/markdown` can be routed by Traefik to `index.md`.
- The Markdown response should use `Content-Type: text/markdown; charset=utf-8`.

## Image Workflow

The original image is kept unchanged. Derived assets can be regenerated with ImageMagick and WebP tools if needed.

Current generated assets:

- `assets/park-oversikt-640.jpg`
- `assets/park-oversikt-640.webp`
- `assets/park-oversikt-960.jpg`
- `assets/park-oversikt-960.webp`
- `assets/park-social-1200x630.jpg`
- `assets/park-social-1200x630.webp`
- `assets/park-sklie-760.jpg`
- `assets/park-sklie-760.webp`
- `assets/park-steiner-760.jpg`
- `assets/park-steiner-760.webp`
- `assets/park-grill-760.jpg`
- `assets/park-grill-760.webp`
- `assets/park-hytte-benk-760.jpg`
- `assets/park-hytte-benk-760.webp`
