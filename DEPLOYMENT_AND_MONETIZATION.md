# Deployment and Monetization Configuration

This outlines exactly how to achieve 100% zero-cost scaling and profitability across the QuickUtils directory using Cloudflare Pages.

## 1. Hosting (Cloudflare Pages)
Cloudflare Pages handles the production execution for this directory architecture completely free of charge.

1. **Link your GitHub Repository** to the Cloudflare dashboard (`H:\boring\projects\tools-directory`).
2. **Build Configuration**:
   - **Framework Preset**: None
   - **Build Command**: `pip install -r requirements.txt && python scripts/fetch_data.py && python scripts/build_directory.py && python scripts/generate_sitemap.py`
   - **Build Output Directory**: `dist`
3. Click "Save and Deploy". Cloudflare will automatically track your `main` branch and redeploy when changes merge.

## 2. DNS & Custom Domains
1. In Cloudflare Pages, go to the project's **Custom Domains** tab.
2. Enter your desired domain name representing your Web Setup Tools sub-brand (e.g. `tools.quickutils.top`).
3. Cloudflare will automatically synthesize the underlying `CNAME` records pointing your top-level namespace to the `{project-name}.pages.dev` target deployment zone.

## 3. Google Analytics 4
1. Obtain your GA4 `G-XXXXXXXX` tag.
2. Simply add it to GitHub as a repository secret or explicit environment variable within Cloudflare Pages named `GA_MEASUREMENT_ID`.
3. The Jinja templates are explicitly designed to natively inject the Google Analytics JavaScript tags when this variable is set. No localized hardcoding necessary.

## 4. Google AdSense Integration
1. Configure an active site property across Google AdSense to generate publisher IDs (`ca-pub-XXXXXXXXX`).
2. In Cloudflare Pages Environment Variables, configure the `ADSENSE_PUBLISHER_ID` to automatically load Google JS units to templates like `item.html`.
3. **ads.txt**: Due to our zero-cost static hosting methodology, `ads.txt` synchronization is completely automated. Cloudflare Pages natively outputs the `dist/ads.txt` created dynamically by our build script using the environmental values.

## 5. Mastodon Social Automation
To establish fully automated SEO distribution through social media, we utilize the Mastodon network.

1. Create a bot-focused Mastodon account across instances like `mastodon.social` or similar free networks.
2. Generate an Access Token via the Mastodon Developer console (`write:statuses` scope required).
3. Set the following two variables in GitHub Secrets to allow GitHub Actions to execute our `post_social.py` command:
   - `MASTODON_ACCESS_TOKEN`
   - `MASTODON_INSTANCE_URL` (Defaults to `mastodon.social`)
4. The system will now run automatically on schedule via `.github/workflows/social-bot.yml` extracting alternatives iteratively completely free.


