# Web Setup Tools Directory
    
**Domain:** [tools.quickutils.top](https://tools.quickutils.top)

A zero-cost static directory archiving web development, setup, and configuration tools.

This project was built automatically using a highly robust Jinja2 templating system, Python ingestion scripts, and purely automated GitHub Actions rendering to Cloudflare Pages.

## Core Features
- **Fuse.js Search**: Instant client-side fuzzy search.
- **RSS/Atom Feed**: Support for content aggregation via `feed.xml`.
- **Network Discovery**: Cross-linking footer for traffic movement between sister sites.
- **Programmatic SEO**: JSON-LD, OpenGraph, and Twitter Card support.
- **Programmatic SEO**: JSON-LD, OpenGraph, and Twitter Card support.
- **Zero-Cost Operation:** Hosted for free on Cloudflare Pages.
- **Dockerized Testing:** Isolated `pytest` suite ensuring >90% code coverage.
- **Automated Social Output:** Python-based Mastodon API bots pushing updates natively.
- **Link Auditing:** Asynchronous URL validation scripts checking HTTP stability internally prior to deployment blockages.
- **Programmatic SEO:** Clean HTML structure, Google Analytics tags, semantic routing, and sitemaps.

## Quick Start
1. Clone this repository.
2. Run `docker compose build test` and `docker compose run --rm test bash -c "pytest --cov=scripts"` to verify the baseline.
3. Edit `data/database.json` to insert new entries matching the keys: `platform, tool_type, pricing`.
4. Run `docker compose up build` to manually generate the `/dist` directory locally.
5. Push to GitHub to instantly trigger `cloudflare-pages.yml`.
