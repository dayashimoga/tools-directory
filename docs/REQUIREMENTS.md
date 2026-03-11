# Project Requirements

## Product Identity
**Target Niche:** Web Setup Tools Directory
**Core Audience:** Individuals and researchers seeking free resources avoiding subscription models.

## Functional Requirements
1. **Static Rendering Pipeline**
   - Must consume JSON arrays containing properties (`title`, `url`, `description`, `platform`, `tool_type`, `pricing`).
   - Must map JSON nodes to category-specific landing pages and individual dynamic item pages.
   - Must output strictly to a static `/dist` HTML compilation without runtime backend processing.
2. **Asynchronous Link Management**
   - The application must validate external URLs to guarantee dead links are rejected securely (`scripts/check_links.py`).
3. **Automated Social Syndication**
   - Programmatically formulate valid Mastodon posts utilizing hashtags extracted dynamically from the JSON payload.
   
## Non-Functional Requirements
1. **Financial Independence (Zero-Cost)**
   - All server processing must be delegated to Cloudflare Pages (free-tier).
   - Domain resolution through Cloudflare DNS.
   - External data hosting (if applicable) through strictly free repositories (e.g. GitHub).
2. **Quality Assurance (>90% Coverage)**
   - All functional scripts encompassing URL checking, rendering logic, social posting, and utility mapping must adhere strictly to >90% code test-coverage.

## Data Schema Rules
- Unique primary constraints on URL fields.
- Specific usage of `platform, tool_type, pricing` to define taxonomy.
