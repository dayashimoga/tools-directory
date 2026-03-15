"""
Shared utilities for the Programmatic SEO Directory.
"""
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Resolve base directories, prioritizing environment variables, then falling back to local paths
DATA_DIR = Path(os.environ.get("DATA_DIR", PROJECT_ROOT / "data"))
if not DATA_DIR.exists() and (PROJECT_ROOT / "projects" / "quickutils-master" / "data").exists():
    DATA_DIR = PROJECT_ROOT / "projects" / "quickutils-master" / "data"

DIST_DIR = Path(os.environ.get("DIST_DIR", PROJECT_ROOT / "dist"))

SRC_DIR = Path(os.environ.get("SRC_DIR", PROJECT_ROOT / "src"))
if not SRC_DIR.exists() and (PROJECT_ROOT / "projects" / "quickutils-master" / "src").exists():
    SRC_DIR = PROJECT_ROOT / "projects" / "quickutils-master" / "src"

TEMPLATES_DIR = SRC_DIR / "templates"

# Dynamic Configuration
CONFIG_PATH = PROJECT_ROOT / "project_config.json"
_CONFIG = {}
if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _CONFIG = json.load(f)
    except Exception:
        pass

# Project Identification
PROJECT_TYPE = str(os.environ.get("PROJECT_TYPE", _CONFIG.get("PROJECT_TYPE", "master")) or "master")

def get_config(key, default):
    # 1. Check environment variable
    val = os.environ.get(key)
    
    # 2. Check project-specific config overrides
    if val is None:
        project_overrides = _CONFIG.get("projects", {}).get(PROJECT_TYPE, {})
        if key in project_overrides:
            val = project_overrides[key]
            
    # 3. Fallback to root level config json and finally default
    if val is None:
        val = _CONFIG.get(key, default)
        
    # Handle boolean strings from environment or config
    if isinstance(val, str):
        if val.lower() in ["true", "yes", "1"]:
            return True
        if val.lower() in ["false", "no", "0"]:
            return False
    return val

# Global Configuration Constants
GH_USERNAME = get_config("GH_USERNAME", "dayashimoga")
GA_MEASUREMENT_ID = get_config("GA_MEASUREMENT_ID", "G-QPDP38ZCCV")
ADSENSE_PUBLISHER_ID = get_config("ADSENSE_PUBLISHER_ID", "ca-pub-5193703345853377")
AMAZON_AFFILIATE_TAG = get_config("AMAZON_AFFILIATE_TAG", "quickutils-20")
GOOGLE_SITE_VERIFICATION = get_config("GOOGLE_SITE_VERIFICATION", "")
PINTEREST_DOMAIN_VERIFY = get_config("PINTEREST_DOMAIN_VERIFY", "c816c2b41079835efd234cb5afef59bf")

# Integration Flags
ENABLE_ADSENSE = get_config("ENABLE_ADSENSE", True)
ENABLE_AMAZON = get_config("ENABLE_AMAZON", True)
ENABLE_PINTEREST = get_config("ENABLE_PINTEREST", True)

# Site Identity
if PROJECT_TYPE == "master" or PROJECT_TYPE == "directory":
    DEFAULT_SITE_URL = "https://quickutils.top"
    DEFAULT_SITE_NAME = "QuickUtils Directory"
else:
    DEFAULT_SITE_URL = f"https://{PROJECT_TYPE}.quickutils.top"
    DEFAULT_SITE_NAME = f"QuickUtils {PROJECT_TYPE.capitalize()} Directory"

SITE_URL = get_config("SITE_URL", DEFAULT_SITE_URL)
SITE_NAME = get_config("SITE_NAME", DEFAULT_SITE_NAME)
SITE_DESCRIPTION = get_config("SITE_DESCRIPTION", f"The Ultimate Directory of Free, Open {PROJECT_TYPE.capitalize()} — searchable and categorized.")


_SLUG_CACHE = {}

def slugify(text: str) -> str:
    """Convert text to a URL-safe slug with caching for performance."""
    if not text:
        return ""
    if text in _SLUG_CACHE:
        return _SLUG_CACHE[text]
        
    # Normalize unicode to ASCII
    n_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # Lowercase
    n_text = n_text.lower()
    # Replace non-alphanumeric with hyphens
    n_text = re.sub(r"[^a-z0-9]+", "-", n_text)
    # Strip leading/trailing hyphens
    n_text = n_text.strip("-")
    # Collapse multiple hyphens
    n_text = re.sub(r"-{2,}", "-", n_text)
    
    _SLUG_CACHE[text] = n_text
    return n_text


def load_database(path: Optional[Path] = None) -> list:
    """Load the database JSON file and return a list of items with optimized slug generation."""
    if path is None:
        path = DATA_DIR / "database.json"

    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError(f"Database at {path} must contain a JSON array")

    # Inject slugs and titles if missing (optimized)
    for item in data:
        title = item.get("title", item.get("name", "Unknown Item"))
        if "title" not in item:
            item["title"] = title
        
        if "slug" not in item:
            # Prefer 'id' if available for stable slugs, otherwise title
            slug_source = str(item.get("id", title))
            item["slug"] = slugify(slug_source)
        
        # Ensure critical fields have defaults for templates
        if "description" not in item:
            item["description"] = "No description provided."
        if "auth" not in item:
            item["auth"] = "None"
        if "cors" not in item:
            item["cors"] = "unknown"
        if "https" not in item:
            item["https"] = True
        if "category" not in item:
            item["category"] = "Uncategorized"
        if "url" not in item:
            item["url"] = "#"
                
    return data


def save_database(items: list, path: Optional[Path] = None) -> bool:
    """Save items to the database JSON file with deterministic sorting.

    Args:
        items: List of item dictionaries.
        path: Optional path. Defaults to data/database.json.
    
    Returns:
        True if saved successfully, False otherwise.
    """
    if path is None:
        path = DATA_DIR / "database.json"

    try:
        ensure_dir(path.parent)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        return True
    except Exception as e:
        print(f"  ✗ Error saving database: {e}")
        return False


def ensure_dir(path: Path) -> None:
    """Create a directory and its parents if they don't exist."""
    path.mkdir(parents=True, exist_ok=True)


def get_categories(items: list) -> dict:
    """Group items by category.

    Args:
        items: List of item dicts, each with a 'category' key.

    Returns:
        Dict mapping category name -> list of items.
    """
    categories = {}
    for item in items:
        cat = item.get("category", "Uncategorized")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)

    # Sort categories alphabetically
    return dict(sorted(categories.items()))


def truncate(text: str, max_length: int = 160) -> str:
    """Truncate text to max_length, adding ellipsis if needed."""
    if not text or len(text) <= max_length:
        return text or ""

    # Ensure we have at least 3 characters room for ellipsis
    limit = int(max(0, max_length - 3))
    trimmed = text[:limit]

    # Try to break at a space to avoid cutting words
    if " " in trimmed:
        return trimmed.rsplit(" ", 1)[0] + "..."
    return trimmed + "..."
