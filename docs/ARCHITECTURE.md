# Technical Architecture - Tools

## System Overview
Tools is part of the QuickUtils network, a programmatic SEO static site ecosystem. It leverages a fully automated pipeline to fetch data, generate optimized static pages, and deploy at zero cost.

## Key Features
- **RSS Feed**: Automatically generated `feed.xml` for content aggregation and distribution.
- **Fuse.js Search**: Instant, client-side fuzzy search for a premium user experience without a backend.
- **Pinterest Automation**: Automated generation of vertical pins and distribution via Mastodon-to-Pinterest bridges.
- **Network Footer**: Cross-linking across the entire QuickUtils ecosystem (9+ niche directories).
- **JSON-LD Schema**: Industry-standard structured data (SoftwareApplication, Dataset, etc.) for rich search snippets.

## Build Pipeline
1. **Fetch**: `fetch_data.py` pulls and normalizes data into `database.json`.
2. **Build**: `build_directory.py` uses Jinja2 to render:
   - Index, Category, and Item pages.
   - `feed.xml` (RSS).
   - `search.json` (Fuse.js index).
3. **SEO**: `generate_sitemap.py` creates `sitemap.xml` and `robots.txt`.
4. **Deploy**: CI/CD pushes to Cloudflare Pages/Netlify.
5. **Social**: `post_social.py` handles daily distribution.

## Monetization
- **AdSense**: Built-in placements with configurable publisher IDs.
- **Carbon Ads**: Native support for ethical developer-focused ads.
- **Affiliates**: Contextual Amazon/Gumroad links.
