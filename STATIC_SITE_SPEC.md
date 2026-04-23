# Static Site Spec

This checklist is for simple static websites: sites made from files that can be served without application logic. A static site can be a marketing page, campaign page, information page, documentation page, organization page, portfolio, landing page, or small public-service page.

The goal is not to force every site into the same voice or feature set. The goal is to make deliberate choices about content, accessibility, indexing, sharing, performance, and optional agent-facing files.

## Tiers

Use these tiers instead of treating every item as mandatory.

### Tier 1: Baseline Static Site

Use for every public static site.

Includes:

- semantic HTML
- responsive CSS
- accessibility basics
- SEO basics
- social sharing metadata when the page may be shared
- image sizing/performance basics
- `robots.txt`
- `sitemap.xml` for public indexed sites
- validation checks

### Tier 2: Trust and Entity Information

Use when the site represents an organization, place, business, public initiative, association, event, venue, or product where identity matters.

Includes:

- official entity name
- registration number when relevant
- address or service area when relevant
- source links for claims that come from external sources
- JSON-LD structured data when the entity is clear

### Tier 3: Agent-Friendly Static Files

Use when agents, crawlers, or automated systems should parse the site more easily, but the site should remain static.

Includes optional files such as:

- `llms.txt`
- `index.md`
- `.well-known/api-catalog`
- `.well-known/agent-skills/index.json`

These files should be truthful. Do not publish metadata for APIs, OAuth, MCP, WebMCP, or tools unless those capabilities actually exist.

### Tier 4: Edge and Hosting Responsibilities

Use at the hosting, proxy, CDN, or edge layer.

Includes:

- HTTPS redirects
- HSTS
- security headers
- cache headers
- compression
- content negotiation
- Markdown-for-agents routing

For example, if Traefik serves different content for `Accept: text/markdown`, that belongs in Traefik or the edge layer, not in the HTML file.

## Scope

A simple static site can be plain files such as:

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

Static sites do not have to use only factual or public-record language. Marketing copy, editorial language, campaign messaging, and brand voice can all belong on static sites.

Still, every site should be clear about what it is. Depending on the project, state:

- site, product, campaign, or organization name
- purpose of the page
- target audience or use case
- address or service area when relevant
- official organization name and registration number when relevant
- contact information if public contact is desired
- source links when claims rely on external sources

Use the right voice for the purpose. A marketing site can be persuasive. A public information site should be precise. A trust-sensitive organization page should avoid claims it cannot support.

## HTML

Use semantic HTML where it fits the content:

- `<!doctype html>`
- `<html lang="...">`
- one primary `<h1>` for the page
- logical heading order with `h2`, `h3`, etc.
- landmarks such as `header`, `nav`, `main`, and `footer`
- content elements such as `section`, `article`, `figure`, `dl`, and `time` when appropriate
- descriptive link text
- image `alt` text
- iframe `title`

References:

- MDN HTML basics: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content
- MDN HTML elements: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements
- MDN document and website structure: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Structuring_documents

Validate with:

- https://validator.w3.org/nu/

## CSS

Keep CSS as simple as the project allows. Framework-free CSS is often enough for small static sites, but a framework can still be appropriate when it matches the project and maintenance model.

Requirements:

- responsive layout
- no horizontal overflow on mobile
- visible focus styles
- sufficient color contrast
- stable dimensions for images and fixed-format UI
- avoid viewport-scaled body text
- account for `prefers-reduced-motion` if animations or transitions are used

References:

- MDN CSS basics: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics
- MDN CSS reference: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference
- MDN responsive design: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design

Validate with:

- https://jigsaw.w3.org/css-validator/

Warnings require judgment. Passing with no errors is usually more important than eliminating every warning from a validator that may not understand every modern feature in context.

## Accessibility

Target WCAG 2.2 AA for public sites.

Minimum checks:

- page language is declared
- headings form a useful outline
- keyboard navigation works
- visible focus outline exists
- contrast is sufficient
- images have appropriate `alt` text
- decorative images have empty `alt` text
- links are descriptive
- iframe has a title
- forms have labels if forms exist
- a skip link is considered when navigation is substantial
- reduced-motion preferences are respected when motion is used

References:

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- MDN accessibility: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Accessibility
- WebAIM contrast checker: https://webaim.org/resources/contrastchecker/

Check with:

- https://wave.webaim.org/
- axe DevTools
- Lighthouse

Automated tools do not prove accessibility. They catch common defects; manual keyboard and screen-reader-oriented review still matters for important sites.

## SEO

Baseline SEO:

- descriptive `<title>`
- useful `<meta name="description">`
- canonical URL for public pages
- semantic headings
- crawlable text content
- `robots.txt`
- `sitemap.xml` for public indexed sites

Optional or situational:

- `<meta name="robots" content="index,follow">` as an explicit default
- JSON-LD structured data when the entity is clear
- `hreflang` for multilingual sites

For local organizations or places, JSON-LD can include:

- name
- description
- canonical URL
- image
- address
- coordinates if known
- maintaining organization if relevant

References:

- Google SEO Starter Guide: https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- Schema.org: https://schema.org/
- MDN document metadata: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/Webpage_metadata

Validate structured data with:

- https://validator.schema.org/
- https://search.google.com/test/rich-results

## Social Sharing

Add Open Graph tags when pages may be shared:

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

Add X/Twitter compatibility tags when useful:

- `twitter:card`
- `twitter:title`
- `twitter:description`
- `twitter:image`

Use a 1200x630 social image when possible.

References:

- Open Graph protocol: https://ogp.me/
- X Cards markup: https://developer.x.com/en/docs/x-for-websites/cards/overview/markup

Check with:

- https://www.opengraph.xyz/
- https://developers.facebook.com/tools/debug/
- https://www.linkedin.com/post-inspector/

## Performance

For static sites, performance should usually be excellent.

Use:

- compressed images
- explicit image `width` and `height`
- `loading="lazy"` for non-critical images
- do not lazy-load the LCP or primary hero image
- `decoding="async"` for non-critical images where appropriate
- no unnecessary JavaScript
- small CSS
- stable layout to avoid CLS

References:

- MDN performance: https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Performance
- web.dev performance: https://web.dev/learn/performance/

Check with:

- https://pagespeed.web.dev/
- https://gtmetrix.com/
- https://www.webpagetest.org/

## Images

Keep original source images unchanged when possible.

Generate derived assets when useful:

- modern formats such as AVIF or WebP when there is a real size benefit
- JPEG or PNG fallback
- 1200x630 image for social sharing

Typical tools:

- ImageMagick: `convert` or `magick`
- WebP: `cwebp`
- AVIF: `avifenc`
- JPEG optimization: `jpegoptim`
- PNG optimization: `optipng`

Use `<picture>` with modern formats first and fallback formats later when there is a real size benefit. Do not add variants that are larger than the original unless there is another clear reason, such as a required social-card crop.

Reference:

- MDN responsive images: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content/HTML_images#responsive_images

## Robots

Create `robots.txt` at the site root for public indexed sites. It should return `200` as `text/plain`.

Minimal example:

```txt
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

AI crawler policy is project-specific. Do not blindly allow or block AI crawlers. Choose intentionally.

Allow-oriented example:

```txt
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Google-Extended
Allow: /
```

Block-oriented example:

```txt
User-agent: GPTBot
Disallow: /

User-agent: Claude-Web
Disallow: /

User-agent: Google-Extended
Disallow: /
```

`Content-Signal` is emerging and not equivalent to RFC 9309 robots rules. Use it only when the project intentionally wants to publish AI content-use preferences.

Example:

```txt
Content-Signal: ai-train=no, search=yes, ai-input=yes
```

References:

- Robots Exclusion Protocol: https://www.rfc-editor.org/rfc/rfc9309
- Content Signals: https://contentsignals.org/

## Sitemap

Create `sitemap.xml` at the site root for public indexed sites. It should return `200` as XML.

Include canonical public URLs. Do not include alternate machine representations such as `index.md` by default unless there is a specific reason to make them indexed/discoverable as independent URLs.

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

- Sitemap protocol: https://www.sitemaps.org/protocol.html

## Agent-Friendly Static Files

These are optional. Add them only when they help the project and can be kept accurate.

Useful static files can include:

- `llms.txt`
- `index.md`
- `.well-known/api-catalog`
- `.well-known/agent-skills/index.json`

### `llms.txt`

Use `llms.txt` as a short machine-readable summary when agent readability matters.

It can include:

- site name
- official entity
- purpose
- address or scope
- coordinates if relevant
- key source links
- static-site scope
- links to Markdown or structured resources

`llms.txt` is a convention, not a replacement for semantic HTML, structured data, or sitemap files.

### `index.md`

Add `index.md` as a maintained Markdown representation of the homepage when agents or downstream systems benefit from Markdown.

If the edge layer supports content negotiation:

- normal `/` requests return `index.html` as `text/html`
- requests with `Accept: text/markdown` can return `index.md`
- Markdown response should use `Content-Type: text/markdown; charset=utf-8`
- response should include `Vary: Accept`

Do not add dynamic Markdown conversion for simple static sites unless there is a clear operational reason.

### Empty Discovery Files

If a scanner expects discovery documents, empty files can be useful only when they truthfully describe the site.

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

These are optional and somewhat scanner-oriented. Do not treat them as universal static-site requirements.

Do not publish OAuth, MCP, API, or WebMCP metadata unless those capabilities actually exist.

## Edge and Security Headers

Security headers normally belong in the hosting or edge layer, not in the static repo.

Handle these in Traefik, Cloudflare, Nginx, Caddy, Apache, Netlify, Vercel, or equivalent:

- HTTPS redirects
- `Strict-Transport-Security`
- `Content-Security-Policy`
- `X-Frame-Options` or CSP `frame-ancestors`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `Cross-Origin-Resource-Policy`
- cache headers
- compression
- content negotiation

CSP must be project-specific and tested against actual assets and third-party origins. A copied CSP can break maps, fonts, forms, analytics, or embeds.

For static repos, document required edge behavior, but do not commit host-specific config unless the host is known and the config is meant to be used.

References:

- MDN HTTP headers: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers
- MDN CSP: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP
- MDN HSTS: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security

Check with:

- https://securityheaders.com/
- https://observatory.mozilla.org/
- https://www.ssllabs.com/ssltest/

## Validation Checklist

Before publishing:

- HTML validates with no errors
- CSS validates with no errors
- validation warnings are reviewed with judgment
- WAVE has no errors
- keyboard navigation is checked manually
- Lighthouse/PageSpeed scores are healthy
- GTmetrix has no major findings
- JSON-LD parses when used
- manifest JSON parses when used
- sitemap XML parses when used
- `robots.txt` returns `200` when used
- `sitemap.xml` returns `200` when used
- `llms.txt` returns `200` when used
- Open Graph preview looks correct when social tags are used
- mobile and desktop layouts are visually checked
- edge headers are checked when the site is deployed

## Git and Publishing

Before editing:

- check `git status`
- identify unrelated dirty worktree changes
- avoid overwriting user or teammate changes

Before committing:

- confirm local git author identity
- check `git status`
- review `git diff --stat`
- commit with a concise message
- push to the correct remote and branch

For organization sites, ensure the commit author and GitHub account are the intended identity.
