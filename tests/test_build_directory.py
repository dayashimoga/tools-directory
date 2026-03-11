"""Tests for scripts/build_directory.py"""
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.build_directory import (
    build_404_page,
    build_category_pages,
    build_index_page,
    build_item_pages,
    build_site,
    copy_static_assets,
    create_jinja_env,
)
from scripts.utils import get_categories


class TestCreateJinjaEnv:
    """Test Jinja2 environment creation."""

    def test_env_created(self, templates_dir):
        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir):
            env = create_jinja_env()
        assert env is not None
        assert "slugify" in env.filters
        assert "truncate_text" in env.filters

    def test_global_variables(self, templates_dir):
        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir):
            env = create_jinja_env()
        assert "site_name" in env.globals
        assert "site_url" in env.globals
        assert "build_date" in env.globals
        assert "current_year" in env.globals


class TestBuildItemPages:
    """Test item page generation."""

    def test_generates_item_files(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_item_pages(env, sample_items, categories)

        item_dir = dist_dir / "item"
        assert item_dir.exists()

        # Check each item has a page
        for item in sample_items:
            page = item_dir / f"{item['slug']}.html"
            assert page.exists(), f"Missing page: {page}"
            content = page.read_text(encoding="utf-8")
            assert item["title"] in content

    def test_item_page_contains_meta(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_item_pages(env, sample_items, categories)

        page = dist_dir / "item" / "nyc-taxi-and-limousine-commission-trip-record-data.html"
        content = page.read_text(encoding="utf-8")
        assert "<title>" in content
        # htmlmin may strip attribute quotes, so check for both forms
        assert 'name="description"' in content or 'name=description' in content
        assert 'rel="canonical"' in content or 'rel=canonical' in content

    def test_item_page_has_related_items(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_item_pages(env, sample_items, categories)

        # Wikipedia and Common Crawl are both Web & Text
        page = dist_dir / "item" / "common-crawl.html"
        content = page.read_text(encoding="utf-8")
        assert "Wikipedia Dumps" in content


class TestBuildCategoryPages:
    """Test category page generation."""

    def test_generates_category_files(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_category_pages(env, categories)

        cat_dir = dist_dir / "category"
        assert cat_dir.exists()
        assert (cat_dir / "transportation.html").exists()
        assert (cat_dir / "web-text.html").exists()

    def test_category_page_contains_items(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_category_pages(env, categories)

        content = (dist_dir / "category" / "web-text.html").read_text(encoding="utf-8")
        assert "Common Crawl" in content
        assert "Wikipedia Dumps" in content


class TestBuildIndexPage:
    """Test homepage generation."""

    def test_generates_index(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_index_page(env, sample_items, categories)

        index = dist_dir / "index.html"
        assert index.exists()

    def test_index_contains_stats(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_index_page(env, sample_items, categories)

        content = (dist_dir / "index.html").read_text(encoding="utf-8")
        assert "4" in content  # total_apis
        assert str(len(categories)) in content

    def test_index_contains_categories(self, tmp_path, templates_dir, sample_items):
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            categories = get_categories(sample_items)
            build_index_page(env, sample_items, categories)

        content = (dist_dir / "index.html").read_text(encoding="utf-8")
        assert "Transportation" in content
        assert "Web &amp; Text" in content


class TestBuild404Page:
    """Test 404 page generation."""

    def test_generates_404(self, tmp_path, templates_dir):
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            env = create_jinja_env()
            build_404_page(env)

        page = dist_dir / "404.html"
        assert page.exists()
        content = page.read_text(encoding="utf-8")
        assert "404" in content


class TestCopyStaticAssets:
    """Test static asset copying."""

    def test_copies_css(self, tmp_path):
        src_dir = tmp_path / "src"
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()

        css_dir = src_dir / "css"
        css_dir.mkdir(parents=True)
        (css_dir / "styles.css").write_text("body{}", encoding="utf-8")

        with patch("scripts.build_directory.SRC_DIR", src_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            copy_static_assets()

        assert (dist_dir / "css" / "styles.css").exists()

    def test_copies_ads_txt(self, tmp_path):
        src_dir = tmp_path / "src"
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        src_dir.mkdir(parents=True)

        (src_dir / "ads.txt").write_text("test", encoding="utf-8")

        with patch("scripts.build_directory.SRC_DIR", src_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            copy_static_assets()

        assert (dist_dir / "ads.txt").exists()

    def test_handles_missing_dirs(self, tmp_path):
        src_dir = tmp_path / "src"
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        src_dir.mkdir(parents=True)

        # Should not raise even with missing css/js/images dirs
        with patch("scripts.build_directory.SRC_DIR", src_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir):
            copy_static_assets()


class TestBuildSite:
    """Test the full build pipeline."""

    def test_full_build(self, tmp_path, templates_dir, sample_database_path):
        dist_dir = tmp_path / "dist"
        src_dir = templates_dir.parent.parent / "src"

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir), \
             patch("scripts.build_directory.SRC_DIR", templates_dir.parent):
            build_site(sample_database_path)

        assert dist_dir.exists()
        assert (dist_dir / "index.html").exists()
        assert (dist_dir / "404.html").exists()
        assert (dist_dir / "feed.xml").exists(), "RSS feed missing"
        assert (dist_dir / "search.json").exists(), "Search index missing"
        assert (dist_dir / "item").is_dir()
        assert (dist_dir / "category").is_dir()

    def test_empty_database(self, tmp_path, templates_dir):
        dist_dir = tmp_path / "dist"
        empty_db = tmp_path / "empty.json"
        empty_db.write_text("[]", encoding="utf-8")

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir), \
             patch("scripts.build_directory.SRC_DIR", templates_dir.parent):
            build_site(empty_db)

        # Should not create dist when database is empty
        assert not (dist_dir / "index.html").exists()

    def test_cleans_old_dist(self, tmp_path, templates_dir, sample_database_path):
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        old_file = dist_dir / "old_file.html"
        old_file.write_text("old", encoding="utf-8")

        with patch("scripts.build_directory.TEMPLATES_DIR", templates_dir), \
             patch("scripts.build_directory.DIST_DIR", dist_dir), \
             patch("scripts.build_directory.SRC_DIR", templates_dir.parent):
            build_site(sample_database_path)

        assert not old_file.exists()
