import json
import os
import sys
from unittest.mock import patch, mock_open, MagicMock

import pytest

from scripts.indexnow_submit import parse_sitemap, submit_to_indexnow, main


def test_parse_sitemap_success():
    xml_data = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>http://example.com/page1</loc></url>
  <url><loc>http://example.com/page2</loc></url>
</urlset>"""
    
    with patch("xml.etree.ElementTree.parse") as mock_parse:
        mock_tree = MagicMock()
        root = MagicMock()
        mock_elem1 = MagicMock()
        mock_elem1.text = "http://example.com/page1"
        mock_elem2 = MagicMock()
        mock_elem2.text = "http://example.com/page2"
        
        root.findall.return_value = [mock_elem1, mock_elem2]
        mock_tree.getroot.return_value = root
        mock_parse.return_value = mock_tree
        
        urls = parse_sitemap("sitemap.xml")
        assert len(urls) == 2
        assert urls[0] == "http://example.com/page1"


def test_parse_sitemap_error():
    with patch("xml.etree.ElementTree.parse", side_effect=Exception("File not found")):
        urls = parse_sitemap("invalid.xml")
        assert urls == []


@patch("scripts.indexnow_submit.urlopen")
def test_submit_to_indexnow_success(mock_urlopen):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_response

    success = submit_to_indexnow("test.com", "key123", ["http://test.com/page1"])
    assert success is True


@patch("scripts.indexnow_submit.urlopen")
def test_submit_to_indexnow_failure_status(mock_urlopen):
    mock_response = MagicMock()
    mock_response.status = 500
    mock_urlopen.return_value.__enter__.return_value = mock_response

    success = submit_to_indexnow("test.com", "key123", ["http://test.com/page1"])
    assert success is False


@patch("scripts.indexnow_submit.urlopen")
def test_submit_to_indexnow_network_error(mock_urlopen):
    mock_urlopen.side_effect = Exception("Network Error")
    success = submit_to_indexnow("test.com", "key123", ["http://test.com/page1"])
    assert success is False


def test_submit_to_indexnow_empty_urls():
    success = submit_to_indexnow("test.com", "key123", [])
    assert success is False


@patch("sys.argv", ["indexnow.py", "https://test.com", "dist", "key123"])
@patch("os.path.exists")
@patch("scripts.indexnow_submit.parse_sitemap")
@patch("scripts.indexnow_submit.submit_to_indexnow")
def test_main_success(mock_submit, mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_parse.return_value = ["http://test.com/page1"]
    mock_submit.return_value = True

    # Should not exit
    main()
    mock_submit.assert_called_once_with("test.com", "key123", ["http://test.com/page1"])


@patch("sys.argv", ["indexnow.py", "https://test.com", "dist", "key123"])
@patch("os.path.exists")
def test_main_no_sitemap(mock_exists):
    mock_exists.return_value = False
    
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


@patch("sys.argv", ["indexnow.py", "https://test.com", "dist", "key123"])
@patch("os.path.exists")
@patch("scripts.indexnow_submit.parse_sitemap")
def test_main_empty_sitemap(mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_parse.return_value = []
    
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


@patch("sys.argv", ["indexnow.py", "https://test.com", "dist", "key123"])
@patch("os.path.exists")
@patch("scripts.indexnow_submit.parse_sitemap")
@patch("scripts.indexnow_submit.submit_to_indexnow")
def test_main_submit_fails(mock_submit, mock_parse, mock_exists):
    mock_exists.return_value = True
    mock_parse.return_value = ["http://test.com/page1"]
    mock_submit.return_value = False
    
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
