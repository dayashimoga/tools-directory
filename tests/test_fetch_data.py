"""Tests for scripts/fetch_data.py"""
import json
from unittest.mock import patch
import pytest
import responses
from scripts.fetch_data import (
    SEED_DATA_URL,
    deduplicate,
    fetch_and_save,
    get_seed_data,
    normalize_entry,
)

class TestNormalizeEntry:
    def test_valid_entry(self):
        raw = {
            "name": "NYC Taxi Data",
            "description": "Public taxi trips",
            "category": "Transportation",
            "url": "https://nyc.gov/",
            "platform": "Parquet",
            "tool_type": "50GB",
            "pricing": "Public Domain"
        }
        result = normalize_entry(raw)
        assert result is not None
        assert result["title"] == "NYC Taxi Data"
        assert result["pricing"] == "Public Domain"

    def test_missing_name_returns_none(self):
        assert normalize_entry({"pricing": "Public Domain"}) is None

    def test_whitespace_trimming(self):
        raw = {"name": "  Trimmed  ", "description": "  Desc  ", "category": "  Test  "}
        result = normalize_entry(raw)
        assert result["title"] == "Trimmed"
        assert result["description"] == "Desc"

class TestDeduplicate:
    def test_removes_duplicates(self):
        items = [
            {"title": "A", "slug": "a"},
            {"title": "A Dup", "slug": "a"},
        ]
        result = deduplicate(items)
        assert len(result) == 1

    def test_sorted_by_title(self):
        items = [{"title": "Z", "slug": "z"}, {"title": "A", "slug": "a"}]
        result = deduplicate(items)
        assert result[0]["title"] == "A"

@responses.activate
def test_successful_fetch(tmp_path):
    responses.add(
        responses.GET,
        "https://api.publicapis.org/entries",
        json={"entries": [{"API": "Test", "Description": "D", "Category": "Test", "Link": "https://t.com"}]},
        status=200,
    )
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path):
        assert fetch_and_save() is True
    assert (tmp_path / "database.json").exists()

@responses.activate
def test_fallback_to_seed_data(tmp_path):
    responses.add(responses.GET, "https://api.publicapis.org/entries", status=500)
    responses.add(responses.GET, "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json", status=500)
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path):
        assert fetch_and_save() is True
    assert (tmp_path / "database.json").exists()

@responses.activate
def test_datasets_filter(tmp_path):
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        json=[{"name": "Data", "description": "D", "category": "Science", "url": "https://t.com"}],
        status=200,
    )
    # Write config file to avoid patching get_config which is used locally
    config_path = tmp_path / "project_config.json"
    config_path.write_text(json.dumps({"PROJECT_TYPE": "datasets"}))
    
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path), \
         patch("scripts.utils.Path.cwd", return_value=tmp_path):
        fetch_and_save()
    items = json.loads((tmp_path / "database.json").read_text())
    assert len(items) == 1

@responses.activate
def test_prompts_filter(tmp_path):
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        json=[{"name": "AI Tool", "description": "D", "category": "Machine Learning", "url": "https://t.com"}],
        status=200,
    )
    config_path = tmp_path / "project_config.json"
    config_path.write_text(json.dumps({"PROJECT_TYPE": "prompts"}))
    
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path), \
         patch("scripts.utils.Path.cwd", return_value=tmp_path):
        fetch_and_save()
    items = json.loads((tmp_path / "database.json").read_text())
    assert len(items) == 1

def test_main_cli_execution():
    with patch("scripts.fetch_data.fetch_and_save", return_value=True) as mock_fetch, \
         patch("scripts.fetch_data.sys.exit") as mock_exit:
        from scripts.fetch_data import main
        main()
        mock_fetch.assert_called_once()
        mock_exit.assert_called_once_with(0)

def test_normalize_entry_edge_cases():
    assert normalize_entry({}) is None
    assert normalize_entry({"name": "No Description"}) is None
    res = normalize_entry({"name": "Auth Test", "description": "D", "Auth": "apiKey", "HTTPS": False})
    assert res["auth"] == "apiKey"
    assert res["https"] is False
    res = normalize_entry({"name": "Defaults", "description": "D"})
    assert res["auth"] == "None"
    assert res["https"] is True


# --- New tests to close coverage gaps ---

@responses.activate
def test_fetch_from_alternative_success():
    """Test fetch_from_alternative returning a valid list."""
    from scripts.fetch_data import fetch_from_alternative
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        json=[{"name": "Alt API", "description": "D", "category": "Test"}],
        status=200,
    )
    result = fetch_from_alternative()
    assert result is not None
    assert len(result) == 1


@responses.activate
def test_fetch_from_alternative_failure():
    """Test fetch_from_alternative returns None on network error."""
    from scripts.fetch_data import fetch_from_alternative
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        status=500,
    )
    assert fetch_from_alternative() is None


@responses.activate
def test_fetch_from_alternative_non_list():
    """Test fetch_from_alternative returns None when response is not a list."""
    from scripts.fetch_data import fetch_from_alternative
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        json={"data": "not a list"},
        status=200,
    )
    assert fetch_from_alternative() is None


@responses.activate
def test_boilerplates_project_type(tmp_path):
    """Cover the boilerplates/opensource branch in fetch_and_save."""
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        json=[
            {"API": "Dev Tool", "Description": "A dev tool", "Category": "Development", "Link": "https://t.com"},
            {"API": "Music API", "Description": "Music stuff", "Category": "Music", "Link": "https://t.com"},
        ],
        status=200,
    )
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path), \
         patch("scripts.utils.get_config", return_value="boilerplates"):
        result = fetch_and_save()
    assert result is True


@responses.activate
def test_cheatsheets_project_type(tmp_path):
    """Cover the cheatsheets branch in fetch_and_save."""
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        json=[
            {"API": "Edu API", "Description": "Learn things", "Category": "Education", "Link": "https://t.com"},
        ],
        status=200,
    )
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path), \
         patch("scripts.utils.get_config", return_value="cheatsheets"):
        result = fetch_and_save()
    assert result is True


@responses.activate
def test_existing_db_preserved_on_total_failure(tmp_path):
    """When all fetches fail AND seed data fails, existing DB should be preserved."""
    responses.add(responses.GET, "https://api.publicapis.org/entries", status=500)
    responses.add(
        responses.GET,
        "https://raw.githubusercontent.com/marcelscruz/public-apis/main/db/data.json",
        status=500,
    )
    # Create existing database with > 5 items
    existing = [{"title": f"Item {i}", "description": "D", "slug": f"item-{i}"} for i in range(10)]
    db_path = tmp_path / "database.json"
    db_path.write_text(json.dumps(existing))

    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path), \
         patch("scripts.fetch_data.get_seed_data", return_value=[]):
        result = fetch_and_save()
    assert result is True  # Preserved existing


@responses.activate
def test_empty_normalized_results(tmp_path):
    """When entries exist but all normalize to None, should return False."""
    responses.add(
        responses.GET,
        "https://api.publicapis.org/entries",
        json={"entries": [{"API": "", "Description": "", "Category": "X"}]},
        status=200,
    )
    with patch("scripts.fetch_data.DATA_DIR", tmp_path), \
         patch("scripts.utils.DATA_DIR", tmp_path):
        result = fetch_and_save()
    assert result is False


def test_main_cli_failure():
    """Test main() when fetch_and_save returns False."""
    with patch("scripts.fetch_data.fetch_and_save", return_value=False), \
         patch("scripts.fetch_data.sys.exit") as mock_exit:
        from scripts.fetch_data import main
        main()
        mock_exit.assert_called_once_with(0)  # Always exits 0


@responses.activate
def test_fetch_from_primary_non_entries():
    """Test fetch_from_primary when response has no 'entries' key."""
    from scripts.fetch_data import fetch_from_primary
    responses.add(
        responses.GET,
        "https://api.publicapis.org/entries",
        json={"data": "wrong key"},
        status=200,
    )
    assert fetch_from_primary() is None

