# Static Site Spec

This checklist is for simple static websites that should be fast, accessible, crawlable, shareable, and usable by AI agents without adding server-side application logic.

## Scope

A simple static site should be plain files that can be served by any static host:

- `index.html`
- `styles.css`
- images/assets
- `robots.txt`
- `sitemap.xml`
- optional `llms.txt`
- optional `index.md`
- optional `.well-known/` discovery files

Do not add dynamic APIs, OAuth/OIDC, MCP servers, WebMCP tools, or application logic unless the project actually needs them.

## Content

Every site should clearly state:

- Site or organization name
- Purpose of the site
- Address or service area when relevant
- Official organization name and registration number when relevant
- Factual claims with source links when claims come from external sources
- Contact information if the organization wants public inquiries

Keep language direct and specific. Avoid vague marketing text when factual public information is more useful.

## HTML

Use semantic HTML:

- `<!doctype html>`
- `<html lang="...">`
- one `<h1>`
- logical heading order with `h2`, `h3`, etc.
- `header`, `nav`, `main`, `section`, `article`, `figure`, `footer`
- descriptive link text
- image `alt` text
- iframe `title`

Validate with:

- https://validator.w3.org/nu/

## CSS

Keep CSS small and framework-free unless the project needs a framework.

Requirements:

- responsive layout
- no horizontal overflow on mobile
- visible focus styles
- sufficient color contrast
- stable image dimensions to avoid layout shift
- avoid viewport-scaled body text

Validate with:

- https://jigsaw.w3.org/css-validator/

## SEO

Add:

- descriptive `<title>`
- useful `<meta name="description">`
- `<meta name="robots" content="index,follow">`
- canonical URL
- semantic headings
- `robots.txt`
- `sitemap.xml`
- JSON-LD structured data when the entity is clear

For local organizations or places, JSON-LD should usually include:

- name
- description
- canonical URL
- image
- address
- coordinates if known
- maintaining organization if relevant

Validate structured data with:

- https://validator.schema.org/
- https://search.google.com/test/rich-results

## Social Sharing

Add Open Graph tags:

- `og:type`
- `og:site_name`
- `og:title`
- `og:description`
- `og:url`
- `og:image`
- `og:image:width`
- `og:image:height`
- `og:image:alt`
- `og:locale`

Add Twitter/X card tags:

- `twitter:card`
- `twitter:title`
- `twitter:description`
- `twitter:image`

Use a 1200x630 social image when possible.

Check with:

- https://www.opengraph.xyz/
- https://developers.facebook.com/tools/debug/
- https://www.linkedin.com/post-inspector/

## Accessibility

Target WCAG 2.2 AA.

Minimum checks:

- no missing alt text
- no empty links or buttons
- clear heading order
- keyboard navigation works
- visible focus outline
- sufficient color contrast
- page language is declared
- iframe has a title

Check with:

- https://wave.webaim.org/
- axe DevTools
- Lighthouse
- https://webaim.org/resources/contrastchecker/

## Performance

For static sites, performance should usually be excellent.

Use:

- compressed images
- explicit image `width` and `height`
- `loading="lazy"` for non-critical images
- `decoding="async"` for images
- no unnecessary JavaScript
- small CSS

Check with:

- https://pagespeed.web.dev/
- https://gtmetrix.com/
- https://www.webpagetest.org/

## Images

Keep the original source image unchanged.

Generate derived assets when useful:

- WebP for modern browsers
- JPEG fallback
- 1200x630 image for social sharing

Typical tools:

- ImageMagick: `convert`
- WebP: `cwebp`
- JPEG optimization: `jpegoptim`

Use `<picture>` with WebP first and JPEG fallback when there is a real size benefit.

## Robots

Create `robots.txt` at the site root. It must return `200` as `text/plain`.

Example:

```txt
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

Content-Signal: ai-train=no, search=yes, ai-input=yes

Sitemap: https://example.com/sitemap.xml
```

Set crawler and AI-training policy intentionally for each project.

Reference:

- https://www.rfc-editor.org/rfc/rfc9309
- https://contentsignals.org/

## Sitemap

Create `sitemap.xml` at the site root. It must return `200` as XML.

Include canonical URLs only.

Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <changefreq>monthly</changefreq>
  </url>
</urlset>
```

Reference:

- https://www.sitemaps.org/protocol.html

## AI Agent Accessibility

For a static site, useful agent-facing files are:

- `llms.txt`
- `index.md`
- `.well-known/api-catalog`
- `.well-known/agent-skills/index.json`

### `llms.txt`

Use `llms.txt` as a short machine-readable summary:

- site name
- official entity
- purpose
- address
- coordinates
- key source links
- static-site scope

### `index.md`

Add `index.md` as a maintained Markdown representation of the homepage.

If the edge layer supports content negotiation:

- normal `/` requests return `index.html` as `text/html`
- requests with `Accept: text/markdown` can return `index.md`
- Markdown response should use `Content-Type: text/markdown; charset=utf-8`

Do not add dynamic Markdown conversion for simple static sites unless there is a clear operational reason.

### Empty Discovery Files

If the site has no API or agent tools, it is acceptable to publish truthful empty discovery files:

`.well-known/api-catalog`

```json
{
  "linkset": []
}
```

`.well-known/agent-skills/index.json`

```json
{
  "$schema": "https://agentskills.io/schemas/agent-skills-index-v0.2.json",
  "skills": []
}
```

Do not publish OAuth, MCP, API, or WebMCP metadata unless those capabilities actually exist.

## Security Headers

Security headers normally belong in the hosting or edge layer, not in the static repo.

Handle these in Traefik, Cloudflare, Nginx, Caddy, Apache, Netlify, Vercel, or equivalent:

- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Frame-Options` or CSP `frame-ancestors`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `Cross-Origin-Resource-Policy`
- cache headers
- compression

For static repos, document the required headers but do not commit host-specific config unless the host is known.

Check with:

- https://securityheaders.com/
- https://observatory.mozilla.org/
- https://www.ssllabs.com/ssltest/

## Validation Checklist

Before publishing:

- HTML validates with no errors
- CSS validates with no errors
- WAVE has no errors
- Lighthouse/PageSpeed scores are healthy
- GTmetrix has no major findings
- JSON-LD parses
- manifest JSON parses
- sitemap XML parses
- `robots.txt` returns `200`
- `sitemap.xml` returns `200`
- `llms.txt` returns `200` if used
- Open Graph preview looks correct
- mobile and desktop layouts are visually checked

## Git/Publishing

Before committing:

- confirm local git author identity
- check `git status`
- review `git diff --stat`
- commit with a concise message
- push to the correct remote and branch

For organization sites, ensure the commit author and GitHub account are the intended identity.
