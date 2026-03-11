"""Tests for scripts/generate_sitemap.py"""
from pathlib import Path

import pytest

from scripts.generate_sitemap import (
    build_robots_txt,
    build_sitemap_xml,
    collect_pages,
    generate_sitemap,
    get_changefreq,
    get_priority,
)


@pytest.fixture
def mock_dist(tmp_path):
    """Create a mock dist directory with HTML files."""
    dist = tmp_path / "dist"
    dist.mkdir()

    # Index
    (dist / "index.html").write_text("<html></html>", encoding="utf-8")

    # API pages
    api_dir = dist / "api"
    api_dir.mkdir()
    (api_dir / "dog-api.html").write_text("<html></html>", encoding="utf-8")
    (api_dir / "cat-facts.html").write_text("<html></html>", encoding="utf-8")

    # Category pages
    cat_dir = dist / "category"
    cat_dir.mkdir()
    (cat_dir / "animals.html").write_text("<html></html>", encoding="utf-8")

    # 404 page (should be excluded from sitemap)
    (dist / "404.html").write_text("<html></html>", encoding="utf-8")

    return dist


class TestCollectPages:
    """Test HTML page collection."""

    def test_collects_all_html(self, mock_dist):
        pages = collect_pages(mock_dist)
        assert len(pages) == 4  # index + 2 api + 1 category (not 404)

    def test_excludes_404(self, mock_dist):
        pages = collect_pages(mock_dist)
        assert "404.html" not in pages

    def test_sorted_output(self, mock_dist):
        pages = collect_pages(mock_dist)
        assert pages == sorted(pages)

    def test_forward_slashes(self, mock_dist):
        pages = collect_pages(mock_dist)
        for page in pages:
            assert "\\" not in page

    def test_empty_directory(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        pages = collect_pages(empty)
        assert pages == []


class TestGetPriority:
    """Test priority assignment."""

    def test_index_highest(self):
        assert get_priority("index.html") == "1.0"

    def test_category_high(self):
        assert get_priority("category/animals.html") == "0.8"

    def test_api_medium(self):
        assert get_priority("api/dog-api.html") == "0.6"

    def test_other_low(self):
        assert get_priority("about.html") == "0.5"


class TestGetChangefreq:
    """Test change frequency assignment."""

    def test_index_weekly(self):
        assert get_changefreq("index.html") == "weekly"

    def test_category_weekly(self):
        assert get_changefreq("category/animals.html") == "weekly"

    def test_api_monthly(self):
        assert get_changefreq("api/dog-api.html") == "monthly"


class TestBuildSitemapXml:
    """Test sitemap XML generation."""

    def test_valid_xml(self):
        pages = ["index.html", "api/test.html"]
        xml = build_sitemap_xml(pages, "https://test.com")
        assert '<?xml version' in xml
        assert "http://www.sitemaps.org/schemas/sitemap/0.9" in xml

    def test_contains_all_urls(self):
        pages = ["index.html", "api/dog.html", "category/animals.html"]
        xml = build_sitemap_xml(pages, "https://test.com")
        assert "https://test.com/" in xml
        assert "https://test.com/api/dog.html" in xml
        assert "https://test.com/category/animals.html" in xml

    def test_index_url_is_root(self):
        pages = ["index.html"]
        xml = build_sitemap_xml(pages, "https://test.com")
        assert "<loc>https://test.com/</loc>" in xml

    def test_contains_lastmod(self):
        pages = ["index.html"]
        xml = build_sitemap_xml(pages, "https://test.com")
        assert "<lastmod>" in xml

    def test_contains_priority(self):
        pages = ["index.html"]
        xml = build_sitemap_xml(pages, "https://test.com")
        assert "<priority>1.0</priority>" in xml

    def test_empty_pages(self):
        xml = build_sitemap_xml([], "https://test.com")
        assert '<?xml version' in xml


class TestBuildRobotsTxt:
    """Test robots.txt generation."""

    def test_contains_sitemap(self):
        result = build_robots_txt("https://test.com")
        assert "Sitemap: https://test.com/sitemap.xml" in result

    def test_allows_all(self):
        result = build_robots_txt("https://test.com")
        assert "User-agent: *" in result
        assert "Allow: /" in result


class TestGenerateSitemap:
    """Test the full sitemap generation pipeline."""

    def test_creates_sitemap_file(self, mock_dist):
        generate_sitemap(mock_dist, "https://test.com")
        assert (mock_dist / "sitemap.xml").exists()

    def test_creates_robots_txt(self, mock_dist):
        generate_sitemap(mock_dist, "https://test.com")
        assert (mock_dist / "robots.txt").exists()

    def test_does_not_overwrite_robots(self, mock_dist):
        # Pre-create robots.txt
        robots = mock_dist / "robots.txt"
        robots.write_text("custom robots", encoding="utf-8")

        generate_sitemap(mock_dist, "https://test.com")

        # Should not overwrite existing robots.txt
        assert robots.read_text(encoding="utf-8") == "custom robots"

    def test_empty_dist_skips(self, tmp_path):
        empty_dist = tmp_path / "empty_dist"
        empty_dist.mkdir()
        generate_sitemap(empty_dist, "https://test.com")
        assert not (empty_dist / "sitemap.xml").exists()

    def test_sitemap_all_pages_included(self, mock_dist):
        generate_sitemap(mock_dist, "https://test.com")
        content = (mock_dist / "sitemap.xml").read_text(encoding="utf-8")
        assert "dog-api.html" in content
        assert "cat-facts.html" in content
        assert "animals.html" in content
