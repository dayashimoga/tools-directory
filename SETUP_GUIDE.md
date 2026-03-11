# Setup Guide

## Local Development
1. **Clone & Install**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Fetch Data**:
   ```bash
   python scripts/fetch_data.py
   ```
3. **Build Site**:
   ```bash
   python scripts/build_directory.py
   python scripts/generate_sitemap.py
   ```
4. **Test**:
   ```bash
   pytest tests/ --cov=scripts
   ```

## Deployment
- Link the repository to **Cloudflare Pages**.
- Set the Build Command: `pip install -r requirements.txt && python scripts/fetch_data.py && python scripts/build_directory.py && python scripts/generate_sitemap.py`
- Set Output Directory: `dist`
