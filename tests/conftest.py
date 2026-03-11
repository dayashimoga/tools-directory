"""
Shared test fixtures for the Programmatic SEO Directory test suite.
"""
import json
import os
import sys
from pathlib import Path

import pytest

# Ensure the project root is in sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_items():
    """A small sample tool for testing."""
    return [
        {
            "title": "NYC Taxi and Limousine Commission Trip Record Data",
            "description": "Taxi trip records",
            "category": "Transportation",
            "url": "https://nyc.gov/",
            "platform": "Parquet / CSV",
            "tool_type": "50GB+",
            "pricing": "Public Domain",
            "slug": "nyc-taxi-and-limousine-commission-trip-record-data",
        },
        {
            "title": "World Bank Open Data",
            "description": "Global development data",
            "category": "Economics & Demographics",
            "url": "https://data.worldbank.org/",
            "platform": "CSV / JSON / XML",
            "tool_type": "Various",
            "pricing": "CC BY 4.0",
            "slug": "world-bank-open-data",
        },
        {
            "title": "Common Crawl",
            "description": "Web crawl data repository",
            "category": "Web & Text",
            "url": "https://commoncrawl.org/",
            "platform": "WARC",
            "tool_type": "Petabytes",
            "pricing": "Open usage terms",
            "slug": "common-crawl",
        },
        {
            "title": "Wikipedia Dumps",
            "description": "Full Wikipedia database dumps",
            "category": "Web & Text",
            "url": "https://dumps.wikimedia.org/",
            "platform": "XML / JSON",
            "tool_type": "20GB+",
            "pricing": "CC BY-SA 4.0",
            "slug": "wikipedia-dumps",
        },
    ]


@pytest.fixture
def sample_database_path(tmp_path, sample_items):
    """Creates a temporary database.json file with sample data."""
    db_path = tmp_path / "database.json"
    db_path.write_text(json.dumps(sample_items, indent=2), encoding="utf-8")
    return db_path


@pytest.fixture
def sample_raw_api_entries():
    """Raw API entries as returned by the public-apis API."""
    return [
        {
            "name": "NYC Taxi trip data",
            "description": "Taxi trip records",
            "category": "Transportation",
            "url": "https://nyc.gov/",
            "platform": "CSV",
            "tool_type": "50GB",
            "pricing": "Public Domain"
        },
        {
            "name": "World Bank Open Data",
            "description": "Global development data",
            "category": "Economics & Demographics",
            "url": "https://data.worldbank.org/",
            "platform": "JSON",
            "tool_type": "Various",
            "pricing": "CC BY 4.0"
        }
    ]


@pytest.fixture
def templates_dir(tmp_path):
    """Creates a temporary templates directory with minimal templates."""
    tpl_dir = tmp_path / "src" / "templates"
    tpl_dir.mkdir(parents=True)

    # Minimal base template
    base = tpl_dir / "base.html"
    base.write_text(
        '<!DOCTYPE html><html lang="en"><head>'
        "<title>{{ page_title }}</title>"
        '<meta name="description" content="{{ page_description }}">'
        '<link rel="canonical" href="{{ canonical_url }}">'
        "</head><body>"
        "{% block content %}{% endblock %}"
        "</body></html>",
        encoding="utf-8",
    )

    # Index template
    index = tpl_dir / "index.html"
    index.write_text(
        '{% extends "base.html" %}'
        "{% block content %}"
        "<h1>{{ site_name }}</h1>"
        "<p>{{ total_apis }} Tools in {{ total_categories }} categories</p>"
        "{% for cat in categories %}"
        '<a href="/category/{{ cat.slug }}.html">{{ cat.name }} ({{ cat.count }})</a>'
        "{% endfor %}"
        "{% for item in featured_items %}"
        '<a href="/item/{{ item.slug }}.html">{{ item.title }}</a>'
        "{% endfor %}"
        "{% endblock %}",
        encoding="utf-8",
    )

    # Item template
    item = tpl_dir / "item.html"
    item.write_text(
        '{% extends "base.html" %}'
        "{% block content %}"
        "<h1>{{ item.title }}</h1>"
        "<p>{{ item.description }}</p>"
        "<p>Category: {{ item.category }}</p>"
        "<p>Platform: {{ item.platform }}</p>"
        "<p>Size: {{ item.tool_type }}</p>"
        "<p>Pricing: {{ item.pricing }}</p>"
        '<a href="{{ item.url }}">Visit</a>'
        "{% for rel in related_items %}"
        '<a href="/item/{{ rel.slug }}.html">{{ rel.title }}</a>'
        "{% endfor %}"
        "{% endblock %}",
        encoding="utf-8",
    )

    # Category template
    category = tpl_dir / "category.html"
    category.write_text(
        '{% extends "base.html" %}'
        "{% block content %}"
        "<h1>{{ category_name }}</h1>"
        "<p>{{ item_count }} Tools</p>"
        "{% for item in items %}"
        '<a href="/item/{{ item.slug }}.html">{{ item.title }}</a>'
        "{% endfor %}"
        "{% for cat in all_categories %}"
        '<a href="/category/{{ cat.slug }}.html">{{ cat.name }}</a>'
        "{% endfor %}"
        "{% endblock %}",
        encoding="utf-8",
    )

    # 404 template
    notfound = tpl_dir / "404.html"
    notfound.write_text(
        '{% extends "base.html" %}'
        "{% block content %}"
        "<h1>404</h1><p>Not Found</p>"
        "{% endblock %}",
        encoding="utf-8",
    )

    return tpl_dir
