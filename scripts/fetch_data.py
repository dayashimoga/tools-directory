"""
Data fetching script for the Web Setup Tools Directory.

This script fetches the latest tools from a JSON source (or uses a seed fallback),
cleans and normalizes them, and saves them to `data/database.json`.
It is designed to be run periodically (e.g., via GitHub Actions) to keep
the directory data up to date automatically.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import requests

from scripts.utils import DATA_DIR, ensure_dir, slugify

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# The primary source for tool data
SEED_DATA_URL = "https://raw.githubusercontent.com/dayashimoga/public-tools-data/main/data.json"


def get_seed_data() -> List[Dict[str, Any]]:
    """Return a hardcoded list of highly valuable public tools."""
    return [
        {
            "name": "NYC Taxi and Limousine Commission Trip Record Data",
            "description": "A comprehensive tool of taxi trips in New York City, including pickup/drop-off dates/times, locations, distances, fares, and passenger counts. Useful for data analysis, machine learning, and mapping projects.",
            "category": "Transportation",
            "url": "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
            "platform": "Parquet / CSV",
            "tool_type": "50GB+",
            "pricing": "Public Domain",
        },
        {
            "name": "World Bank Open Data",
            "description": "Free and open access to global development data including population patterns, GDP, life expectancy, poverty rates, education, and carbon emissions across all nations.",
            "category": "Economics & Demographics",
            "url": "https://data.worldbank.org/",
            "platform": "CSV / JSON / XML",
            "tool_type": "Various",
            "pricing": "CC BY 4.0",
        },
        {
            "name": "Common Crawl",
            "description": "An open repository of web crawl data that can be accessed and analyzed by anyone. Contains petabytes of data collected over many years, widely used for training LLMs.",
            "category": "Web & Text",
            "url": "https://commoncrawl.org/",
            "platform": "WARC / WAT / WET",
            "tool_type": "Petabytes",
            "pricing": "Open usage terms",
        },
        {
            "name": "Hugging Face Tools",
            "description": "A massive repository of community-contributed tools primarily focused on Natural Language Processing (NLP), Computer Vision, and Audio AI tasks.",
            "category": "Machine Learning",
            "url": "https://huggingface.co/docs/tools",
            "platform": "Various via Library",
            "tool_type": "Various",
            "pricing": "Varies by tool",
        },
        {
            "name": "NASA Earth Data",
            "description": "Open access to a vast array of Earth science data ranging from satellite imagery, climate monitoring, atmospheric phenomena, and oceans.",
            "category": "Climate & Space",
            "url": "https://earthdata.nasa.gov/",
            "platform": "HDF / NetCDF / GeoTIFF",
            "tool_type": "Petabytes",
            "pricing": "Public Domain",
        }
    ]


def normalize_entry(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize a raw tool entry from the public schema to our internal schema.

    Returns:
        A normalized dictionary, or None if the entry is invalid (missing title).
    """
    raw_title = entry.get("name", "")
    if not str(raw_title).strip():
        return None  # Title is absolutely required

    title = str(raw_title).strip()
    slug = slugify(title)
    if not slug:
        return None

    # Handle descriptions
    desc = str(entry.get("description", "")).strip()
    if not desc:
        desc = "No description provided."

    # Handle other tool-specific metadata
    category = str(entry.get("category", "Uncategorized")).strip()
    url = str(entry.get("url", "")).strip()
    tool_platform = str(entry.get("platform", "Unknown")).strip()
    tool_type = str(entry.get("tool_type", "Unknown")).strip()
    pricing_type = str(entry.get("pricing", "Unknown")).strip()

    normalized = {
        "title": title,
        "description": desc,
        "category": category,
        "url": url,
        "slug": slug,
        "platform": tool_platform,  # e.g., CSV, JSON, Parquet
        "tool_type": tool_type,            # e.g., 5GB, 100MB
        "pricing": pricing_type  # e.g., Public Domain, CC-BY
    }

    return normalized


def deduplicate(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate items based on slug and sort alphabetically."""
    seen = set()
    unique = []
    for item in items:
        if item["slug"] not in seen:
            seen.add(item["slug"])
            unique.append(item)
    return sorted(unique, key=lambda x: x["title"].casefold())


def get_remote_data() -> Optional[List[Dict[str, Any]]]:
    """Attempt to fetch tool entries from a central repository."""
    try:
        logger.info(f"Fetching from tool API: {SEED_DATA_URL}...")
        resp = requests.get(SEED_DATA_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            logger.info(f"Found {len(data)} remote items.")
            return data
        return None
    except requests.RequestException as e:
        logger.warning(f"Error fetching from {SEED_DATA_URL}: {e}")
        return None
    except ValueError:
        logger.warning("Response was not a valid JSON array.")
        return None


def fetch_and_save() -> bool:
    """Main pipeline to fetch, clean, platform, and save data.

    Returns:
        True if data was successfully saved, False otherwise.
    """
    raw_entries = get_remote_data()

    if not raw_entries:
        # Preserve existing database.json if it has real data
        db_path = DATA_DIR / "database.json"
        if db_path.exists():
            try:
                import json as _json
                existing = _json.loads(db_path.read_text(encoding="utf-8"))
                if isinstance(existing, list) and len(existing) > 5:
                    logger.info(f"Remote fetch failed but existing database has {len(existing)} items. Keeping existing data.")
                    return True
            except Exception:
                pass
        logger.warning("Could not fetch remote tools. Falling back to built-in seed data.")
        raw_entries = get_seed_data()

    # Normalize entries
    normalized = []
    for entry in raw_entries:
        norm = normalize_entry(entry)
        if norm:
            normalized.append(norm)

    if not normalized:
        logger.error("No valid tool entries could be parsed.")
        return False

    # Deduplicate
    final_items = deduplicate(normalized)
    logger.info(f"Processed {len(final_items)} unique static tools.")

    # Save to JSON
    ensure_dir(DATA_DIR)
    db_path = DATA_DIR / "database.json"

    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(final_items, f, indent=2, sort_keys=True)
        logger.info(f"Successfully saved to {db_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to write database: {e}")
        return False


if __name__ == "__main__":
    success = fetch_and_save()
    if not success:
        import sys
        sys.exit(1)
