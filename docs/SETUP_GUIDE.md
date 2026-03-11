# Setup & Configuration Guide

This guide covers every step to deploy and configure the QuickUtils API Directory from scratch.

---

## Table of Contents

1. [Google Analytics (GA4)](#1-google-analytics-ga4)
2. [Google AdSense](#2-google-adsense)
3. [Amazon Associates (Affiliates)](#3-amazon-associates-affiliates)
4. [Mastodon Social Bot](#4-mastodon-social-bot)
5. [Netlify Deployment](#5-netlify-deployment)
6. [Custom Domain & SSL](#6-custom-domain--ssl)
7. [Alternative Hosting](#7-alternative-hosting-backup-options)
8. [Environment Variables Reference](#8-environment-variables-reference)

---

## 1. Google Analytics (GA4)

Google Analytics tracks visitor behavior, page views, traffic sources, and more.

### Step-by-Step

1. **Create a Google Analytics Account**
   - Go to [analytics.google.com](https://analytics.google.com)
   - Click **Start measuring** â†’ Create Account
   - Name: `QuickUtils` â†’ Next

2. **Create a Property**
   - Property name: `API Directory`
   - Timezone and currency: your local settings
   - Click **Next** â†’ Select business info â†’ **Create**

3. **Set Up Data Stream**
   - Choose **Web**
   - Website URL: `https://directory.quickutils.top`
   - Stream name: `API Directory`
   - Click **Create stream**

4. **Get Your Measurement ID**
   - After creating the stream, you'll see a Measurement ID like `G-ABC123XYZ`
   - Copy this ID

5. **Configure the Project**
   - Set the environment variable in your Netlify dashboard or `.env` file:
     ```
     GA_MEASUREMENT_ID=G-ABC123XYZ
     ```
   - The GA tracking script in `base.html` automatically loads when this is set.
   - **No code changes needed** â€” the template conditionally loads GA only when a real ID is present.

6. **Verify Installation**
   - Open your site in a browser
   - Go to GA4 â†’ **Realtime** report
   - You should see yourself as an active user

> **Note**: GA is free for up to 10 million hits/month. You'll never exceed this on a static directory site.

---

## 2. Google AdSense

AdSense displays contextual ads on your pages and pays you per click/impression.

### Prerequisites
- Your site must have **original content** and be **publicly accessible**
- Google typically requires **~30 pages** of unique content (we have 46+)
- Site should be **at least 3 months old** (some regions have no waitThe period)

### Step-by-Step

1. **Sign Up for AdSense**
   - Go to [adsense.google.com](https://adsense.google.com/start)
   - Sign in with your Google account
   - Enter your website URL: `https://directory.quickutils.top`
   - Select your country â†’ Accept terms

2. **Get Your Publisher ID**
   - After approval, go to **Account** â†’ **Account Information**
   - Your Publisher ID looks like `ca-pub-1234567890123456`

3. **Configure the Project**
   ```
   ADSENSE_PUBLISHER_ID=ca-pub-1234567890123456
   ```

4. **Create Ad Units**
   - In AdSense dashboard â†’ **Ads** â†’ **By ad unit**
   - Create a **Display ad** (responsive)
   - Copy the `data-ad-slot` value

5. **Update Ad Slot IDs in Templates**
   - In `item.html` and `category.html`, replace `XXXXXXXXXX` with your actual ad slot IDs
   - Different slot IDs for different positions (in-content, sidebar, below featured)

6. **ads.txt Verification**
   - The `src/ads.txt` file is already created. Update the publisher ID:
     ```
     google.com, pub-1234567890123456, DIRECT, f08c47fec0942fa0
     ```
   - This file is automatically copied to `dist/ads.txt` during build

### Revenue Expectations

| Traffic (monthly) | Estimated Revenue |
|---|---|
| 1,000 visitors | $1-5 |
| 10,000 visitors | $20-80 |
| 50,000 visitors | $100-400 |
| 100,000 visitors | $300-1,200 |

> Actual revenue depends on niche (developer tools = higher CPC), geography, and ad placement.

---

## 3. Amazon Associates (Affiliates)

The directory shows curated programming book recommendations on API detail pages, earning commission on purchases.

### Step-by-Step

1. **Sign Up for Amazon Associates**
   - Go to [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
   - Click **Join Now for Free**
   - Enter your account info, website URL, and preferred Store ID

2. **Get Your Tracking Tag**
   - After signup, your tag looks like `yourtag-20`
   - This is appended to all Amazon links as `?tag=yourtag-20`

3. **Configure the Project**
   ```
   AMAZON_AFFILIATE_TAG=yourtag-20
   ```

4. **How It Works**
   - `build_directory.py` contains `BOOK_RECOMMENDATIONS` â†’ a dict mapping API categories to curated books
   - Each book has a title, author, and ASIN (Amazon product ID)
   - During build, Amazon URLs are generated: `https://www.amazon.com/dp/{ASIN}?tag={your-tag}`
   - Books appear in the item page sidebar under "ðŸ“š Recommended Books"

5. **Adding More Books**
   - Edit `BOOK_RECOMMENDATIONS` in `scripts/build_directory.py`
   - Find the ASIN on any Amazon product page (in the URL after `/dp/`)
   - Add entries with `title`, `author`, and `asin` keys

6. **FTC Disclosure**
   - The affiliate disclosure is automatically included: *"As an Amazon Associate we earn from qualifying purchases."*
   - This is **legally required** by the FTC and Amazon Associates program

### Commission Rates

| Category | Commission |
|---|---|
| Books (physical) | 4.5% |
| Books (Kindle) | 4.5% |
| Software | 5% |
| Electronics | 4% |

> **Important**: Amazon requires you to make at least 3 qualifying sales within 180 days of signing up, or your account will be closed. Make sure you have traffic before applying.

---

## 4. Mastodon Social Bot

The bot posts a random API from the directory to Mastodon daily, driving traffic back to your site.

### Step-by-Step

1. **Create a Mastodon Account**
   - Sign up at [mastodon.social](https://mastodon.social) or any instance
   - Verify your email and complete profile

2. **Create an Application (API Token)**
   - Go to **Preferences** â†’ **Development** â†’ **New Application**
   - Application name: `QuickUtils Bot`
   - Scopes: check `write:statuses` only
   - Click **Submit**
   - Open the created application â†’ copy **Your access token**

3. **Add Secrets to GitHub**
   - Go to your GitHub repo â†’ **Settings** â†’ **Secrets and variables** â†’ **Actions**
   - Add these secrets:
     ```
     MASTODON_ACCESS_TOKEN=your-access-token-here
     MASTODON_INSTANCE_URL=mastodon.social
     ```

4. **Test Manually**
   - Go to **Actions** â†’ **Social Media Bot** â†’ **Run workflow**
   - Check your Mastodon profile for the post

5. **Customize Posts**
   - Edit `scripts/post_social.py` â†’ `format_post()` function
   - Hashtags, link format, and description are all configurable

---

## 5. Netlify Deployment

Netlify automatically builds and deploys your site when you push to GitHub.

### Step-by-Step

1. **Push to GitHub**
   ```bash
   git init
   git add -A
   git commit -m "Initial commit: API Directory"
   git remote add origin https://github.com/YOUR_USERNAME/quickutils-directory.git
   git push -u origin main
   ```

2. **Connect to Netlify**
   - Sign in at [netlify.com](https://app.netlify.com)
   - Click **Add new site** â†’ **Import an existing project**
   - Choose **GitHub** â†’ Authorize â†’ Select your repo

3. **Build Settings** (auto-detected from `netlify.toml`)
   - Build command: `pip install -r requirements.txt && python -m scripts.build_directory && python -m scripts.generate_sitemap`
   - Publish directory: `dist`
   - These are already configured in `netlify.toml`

4. **Environment Variables**
   - Go to **Site settings** â†’ **Environment variables**
   - Add all variables from the [reference table](#8-environment-variables-reference)

5. **Deploy**
   - Click **Deploy site**. First deployment takes ~2 minutes
   - Netlify assigns a random URL like `https://xyz-123.netlify.app`

### Build Minutes Budget

| Activity | Minutes/month |
|---|---|
| Weekly data sync (4 builds) | ~8 min |
| Manual re-deploys | ~2 min each |
| **Total** | **~10 of 300 free** |

> **Warning**: Avoid triggering unnecessary builds. The `data-sync.yml` workflow only commits and pushes if data actually changed.

---

## 6. Custom Domain & SSL

### Configure Subdomain (Recommended)

Using `directory.quickutils.top` keeps your main domain free.

1. **In Netlify**: Settings â†’ Domain management â†’ Add custom domain
   - Enter: `directory.quickutils.top`

2. **In your DNS provider** (wherever you registered `quickutils.top`):
   - Add a **CNAME** record:
     | Type | Name | Value | TTL |
     |---|---|---|---|
     | CNAME | `directory` | `xyz-123.netlify.app` | Auto |

3. **SSL Certificate**
   - Netlify provides **free SSL via Let's Encrypt** automatically
   - Go to Settings â†’ Domain management â†’ HTTPS â†’ Verify DNS â†’ Provision certificate
   - Takes 5-15 minutes to activate
   - Force HTTPS is enabled by default

### Configure Root Domain

If using the root domain (`quickutils.top`) instead:

1. In Netlify: Add `quickutils.top` as custom domain
2. In DNS provider:
   - Add an **A record** pointing to Netlify's load balancer:
     | Type | Name | Value |
     |---|---|---|
     | A | `@` | `75.2.60.5` |
   - Add a **CNAME** for `www`:
     | Type | Name | Value |
     |---|---|---|
     | CNAME | `www` | `xyz-123.netlify.app` |

### Verify DNS Propagation

```bash
# Check CNAME
dig directory.quickutils.top CNAME

# Check if accessible
curl -I https://directory.quickutils.top
```

DNS propagation can take up to 48 hours, but typically completes within 1-2 hours.

---

## 7. Alternative Hosting (Backup Options)

If Netlify doesn't work out, here are free alternatives that support static sites:

### Cloudflare Pages (Primary â€” Recommended)

| Feature | Details |
|---|---|
| **Free tier** | 500 builds/month, unlimited bandwidth, unlimited sites |
| **Build command** | Same as Netlify |
| **SSL** | Free, automatic |

#### Step 1: Get Your Cloudflare Account ID

1. Sign up at [cloudflare.com](https://www.cloudflare.com/) (free)
2. After login, look at the URL in your browser: `dash.cloudflare.com/0038891404c0d165f973715c6130eb5a`
3. The string after `dash.cloudflare.com/` is your **Account ID**: `0038891404c0d165f973715c6130eb5a`
4. Or: click your profile icon â†’ **Account Home** â†’ find Account ID in the right sidebar

#### Step 2: Create a Cloudflare API Token

1. Go to [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens)
2. Click **Create Token**
3. Use the **"Edit Cloudflare Workers"** template (or create custom)
4. For custom token, grant these permissions:
   - **Account** â†’ **Cloudflare Pages** â†’ **Edit**
   - **Zone** â†’ **DNS** â†’ **Edit** (if managing DNS via Cloudflare)
5. Click **Continue to summary** â†’ **Create Token**
6. **Copy the token immediately** â€” you won't see it again

#### Step 3: Add Secrets to GitHub

1. Go to your GitHub repo â†’ **Settings** â†’ **Secrets and variables** â†’ **Actions**
2. Add **Repository secrets**:
   ```
   CLOUDFLARE_API_TOKEN = (Your generated token from the "Edit Cloudflare Workers" template)
   CLOUDFLARE_ACCOUNT_ID = 0038891404c0d165f973715c6130eb5a
   ```

#### Step 4: Deploy (Automatic)

Push to `main` â†’ the `.github/workflows/cloudflare-pages.yml` workflow automatically:
1. Builds the Python site
2. Deploys to Cloudflare Pages via `wrangler pages deploy`
3. Assigns a URL like `https://quickutils-directory.pages.dev`

#### Step 5: Set Up `directory.quickutils.top` (Porkbun DNS)

Since your domain is on **Porkbun**:

1. Log in to [porkbun.com](https://porkbun.com/)
2. Go to **Domain Management** â†’ click `quickutils.top` â†’ **DNS Records**
3. Click **Add Record** with these settings:

   | Field | Value |
   |---|---|
   | **Type** | `CNAME` |
   | **Host** | `directory` |
   | **Answer** | `quickutils-directory.pages.dev` |
   | **TTL** | `600` (or Auto) |

4. Click **Add**

5. In Cloudflare Pages:
   - Go to your project â†’ **Custom domains** â†’ **Set up a custom domain**
   - Enter: `directory.quickutils.top`
   - Cloudflare will verify the CNAME record (takes 1-5 minutes)
   - SSL certificate is provisioned automatically

#### Verify Setup

```bash
# Check CNAME record
nslookup directory.quickutils.top

# Should show: quickutils-directory.pages.dev
# (Confirmed active on quickutils.top via nslookup)

# Check HTTPS
curl -I https://directory.quickutils.top
```

> **Note**: DNS propagation takes 5-60 minutes with Porkbun. If it doesn't work immediately, wait and retry.

### GitHub Pages

| Feature | Details |
|---|---|
| **Free tier** | Unlimited, 100 GB bandwidth/month |
| **Limitation** | No server-side build â€” need GitHub Actions to build first |
| **Setup** | Use a GitHub Action to build and push to `gh-pages` branch |

Steps:
1. Add a workflow `.github/workflows/gh-pages.yml`:
   ```yaml
   name: Deploy to GitHub Pages
   on:
     push:
       branches: [main]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: actions/setup-python@v5
           with:
             python-version: '3.11'
         - run: pip install -r requirements.txt
         - run: python -m scripts.build_directory
         - run: python -m scripts.generate_sitemap
         - uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./dist
   ```
2. Settings â†’ Pages â†’ Source: `gh-pages` branch

### Vercel

| Feature | Details |
|---|---|
| **Free tier** | 6000 build minutes/month, 100 GB bandwidth |
| **Limitation** | Python builds need custom setup |
| **Setup** | [vercel.com](https://vercel.com) â†’ Import project â†’ Set build command |

### Render

| Feature | Details |
|---|---|
| **Free tier** | Static sites are free, 400 build hours/month |
| **Setup** | [render.com](https://render.com) â†’ New â†’ Static Site â†’ Connect repo |

Build command: `pip install -r requirements.txt && python -m scripts.build_directory && python -m scripts.generate_sitemap`
Publish directory: `dist`

---

## 8. Environment Variables Reference

| Variable | Required | Default | Where to Set |
|---|---|---|---|
| `SITE_URL` | No | `https://directory.quickutils.top` | Netlify env vars |
| `GA_MEASUREMENT_ID` | No | `G-XXXXXXXXXX` (disabled) | Netlify env vars |
| `ADSENSE_PUBLISHER_ID` | No | `ca-pub-XXXXXXXXXX` (disabled) | Netlify env vars |
| `AMAZON_AFFILIATE_TAG` | No | `quickutils-20` | Netlify env vars |
| `MASTODON_ACCESS_TOKEN` | For bot | â€” | GitHub repo secrets |
| `MASTODON_INSTANCE_URL` | For bot | `mastodon.social` | GitHub repo secrets |

> **Security**: Never commit secrets to your repo. Use Netlify environment variables for build-time config and GitHub Secrets for Action workflows.


