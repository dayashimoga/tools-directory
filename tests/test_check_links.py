"""Tests for scripts/check_links.py"""
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError

from scripts.check_links import check_url, generate_report, main_async


@pytest.fixture
def mock_db_items():
    return [
        {"title": "Valid Item", "url": "https://valid.com", "github_repo": "https://github.com/valid/valid"},
        {"title": "Broken Item", "url": "https://broken.com", "github_repo": "https://github.com/broken/broken"},
        {"title": "Missing URL", "url": "", "github_repo": ""}, # Won't be checked
    ]


@pytest.mark.asyncio
class TestCheckUrl:
    """Tests for the individual URL checking function."""

    async def test_empty_url(self):
        url, is_valid, error = await check_url(MagicMock(), "")
        assert not is_valid
        assert "Empty URL" in error

    async def test_head_success(self):
        mock_response = AsyncMock()
        mock_response.status = 200
        
        mock_ctx = AsyncMock()
        mock_ctx.__aenter__.return_value = mock_response
        mock_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.head.return_value = mock_ctx

        url, is_valid, error = await check_url(session=mock_session, url="https://test.com")
        assert is_valid
        assert not error

    async def test_head_fails_fallback_to_get_success(self):
        mock_head_resp = AsyncMock()
        mock_head_resp.status = 407  # Force fallback
        mock_head_ctx = AsyncMock()
        mock_head_ctx.__aenter__.return_value = mock_head_resp
        mock_head_ctx.__aexit__.return_value = None
        
        mock_get_resp = AsyncMock()
        mock_get_resp.status = 200
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__.return_value = mock_get_resp
        mock_get_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.head.return_value = mock_head_ctx
        mock_session.get.return_value = mock_get_ctx

        url, is_valid, error = await check_url(mock_session, "https://test.com")
        assert is_valid
        assert not error

    async def test_head_fails_fallback_to_get_fails(self):
        mock_head_resp = AsyncMock()
        mock_head_resp.status = 407
        mock_head_ctx = AsyncMock()
        mock_head_ctx.__aenter__.return_value = mock_head_resp
        mock_head_ctx.__aexit__.return_value = None
        
        mock_get_resp = AsyncMock()
        mock_get_resp.status = 407
        mock_get_ctx = AsyncMock()
        mock_get_ctx.__aenter__.return_value = mock_get_resp
        mock_get_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.head.return_value = mock_head_ctx
        mock_session.get.return_value = mock_get_ctx

        url, is_valid, error = await check_url(mock_session, "https://test.com")
        assert not is_valid
        assert "GET returned HTTP 407" in error

    async def test_timeout_error(self):
        import asyncio
        mock_head_ctx = AsyncMock()
        mock_head_ctx.__aenter__.side_effect = asyncio.TimeoutError()
        mock_head_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.head.return_value = mock_head_ctx

        url, is_valid, error = await check_url(mock_session, "https://test.com")
        assert is_valid
        assert "Treated as WAF mitigation" in error

    async def test_client_error(self):
        mock_head_ctx = AsyncMock()
        mock_head_ctx.__aenter__.side_effect = ClientError("Test network error")
        mock_head_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.head.return_value = mock_head_ctx

        url, is_valid, error = await check_url(mock_session, "https://test.com")
        assert is_valid
        assert "Treated as WAF mitigation" in error

    async def test_unexpected_error(self):
        mock_head_ctx = AsyncMock()
        mock_head_ctx.__aenter__.side_effect = ValueError("Some weird error")
        mock_head_ctx.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.head.return_value = mock_head_ctx

        url, is_valid, error = await check_url(mock_session, "https://test.com")
        assert not is_valid
        assert "Unexpected error: Some weird error" in error


@pytest.mark.asyncio
class TestMainAsync:
    """Tests for the main asynchronous process."""

    @patch("scripts.check_links.DB_PATH")
    async def test_database_not_found(self, mock_db_path, caplog):
        mock_db_path.exists.return_value = False
        with pytest.raises(SystemExit) as exc:
            await main_async(fail_fast=False)
        assert exc.value.code == 1
        assert "Database not found" in caplog.text

    @patch("scripts.check_links.DB_PATH")
    async def test_invalid_json(self, mock_db_path, caplog, tmp_path):
        db_file = tmp_path / "db.json"
        db_file.write_text("{invalid_json: true}")
        mock_db_path.exists.return_value = True

        with patch("builtins.open", return_value=db_file.open("r")):
            with pytest.raises(SystemExit) as exc:
                await main_async(fail_fast=False)
            assert exc.value.code == 1
            assert "Failed to parse" in caplog.text

    @patch("scripts.check_links.DB_PATH")
    @patch("scripts.check_links.check_url")
    async def test_all_links_valid(self, mock_check_url, mock_db_path, mock_db_items, tmp_path):
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps(mock_db_items))
        mock_db_path.exists.return_value = True

        # Mock check_url to always return valid
        async def mock_valid(session, url):
            return url, True, ""
        mock_check_url.side_effect = mock_valid
        
        with patch("builtins.open", return_value=db_file.open("r", encoding="utf-8")):
            total_items, total, broken, all_results, _ = await main_async(fail_fast=False)
            
            assert total_items == 3
            assert total == 4 # 2 valid, 2 broken (total 4 urls in mock)
            assert broken == 0
            assert len(all_results) == 4

    @patch("scripts.check_links.DB_PATH")
    @patch("scripts.check_links.check_url")
    async def test_broken_links_found(self, mock_check_url, mock_db_path, mock_db_items, tmp_path):
        db_file = tmp_path / "db.json"
        db_file.write_text(json.dumps(mock_db_items))
        mock_db_path.exists.return_value = True

        # Mock check_url to return invalid for 'broken'
        async def mock_mixed(session, url):
            if "broken.com" in url or "broken/broken" in url:
                return url, False, "HTTP 407"
            return url, True, ""
        mock_check_url.side_effect = mock_mixed
        
        with patch("builtins.open", return_value=db_file.open("r", encoding="utf-8")):
            total_items, total, broken, all_results, _ = await main_async(fail_fast=False)
            
            assert total_items == 3
            assert total == 4
            assert broken == 2
            assert len(all_results) == 4


class TestGenerateReport:
    """Tests for report generation logic."""

    def test_clean_report(self):
        report_text = generate_report(total_items=15, total=10, broken=0, all_results=[], url_to_titles={})
        assert "Total Database Items Scanned:** 15" in report_text
        assert "Total Links Checked:** 10" in report_text
        assert "Healthy Links:** 10" in report_text
        assert "Broken Links:** 0" in report_text

    def test_comprehensive_report(self):
        results = [("https://bad.com", False, "407"), ("https://good.com", True, "200")]
        mapping = {"https://bad.com": ["Item 1"]}
        report_text = generate_report(total_items=20, total=10, broken=1, all_results=results, url_to_titles=mapping)
        assert "Total Database Items Scanned:** 20" in report_text
        assert "Total Links Checked:** 10" in report_text
        assert "Broken Links:** 1" in report_text
        assert "All Links Evaluated" in report_text
        assert "https://bad.com" in report_text
        assert "❌ Fail" in report_text


class TestMainCLI:
    """Tests for the command-line interface entry point."""

    @patch("scripts.check_links.main_async")
    @patch("scripts.check_links.argparse.ArgumentParser.parse_args")
    def test_success_exit(self, mock_args, mock_async):
        mock_args.return_value = MagicMock(fail_fast=False, output_report=None)
        
        async def mock_success(*args, **kwargs):
            return 5, 10, 0, [], {}
        mock_async.side_effect = mock_success

        from scripts.check_links import main
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

    @patch("scripts.check_links.main_async")
    @patch("scripts.check_links.argparse.ArgumentParser.parse_args")
    def test_failure_exit_with_report(self, mock_args, mock_async, tmp_path):
        report_file = tmp_path / "report.md"
        mock_args.return_value = MagicMock(fail_fast=False, output_report=str(report_file))
        
        async def mock_fail(*args, **kwargs):
            return 5, 10, 1, [("https://bad.com", False, "407")], {"https://bad.com": ["Item 1"]}
        mock_async.side_effect = mock_fail

        from scripts.check_links import main
        with pytest.raises(SystemExit) as exc:
            main()
            
        assert exc.value.code == 1
        assert report_file.exists()
        assert "All Links Evaluated" in report_file.read_text(encoding="utf-8")
