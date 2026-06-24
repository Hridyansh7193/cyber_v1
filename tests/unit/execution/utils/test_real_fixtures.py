import pytest
from pathlib import Path
from execution.utils.output_parser import OutputParser

FIXTURES_DIR = Path(__file__).parent.parent.parent.parent / "fixtures" / "real_outputs"

def test_subfinder_fixture():
    content = (FIXTURES_DIR / "subfinder.txt").read_text(encoding="utf-8")
    lines = OutputParser.parse_lines(content)
    assert len(lines) == 3
    assert "api.example.com" in lines

def test_httpx_fixture():
    content = (FIXTURES_DIR / "httpx.json").read_text(encoding="utf-8")
    items = OutputParser.parse_json(content)
    assert len(items) == 2
    assert items[0]["request"]["endpoint"] == "http://api.example.com"

def test_katana_fixture():
    content = (FIXTURES_DIR / "katana.json").read_text(encoding="utf-8")
    items = OutputParser.parse_json(content)
    assert len(items) == 2
    assert items[1]["response"]["status_code"] == 401

def test_nuclei_fixture():
    content = (FIXTURES_DIR / "nuclei.json").read_text(encoding="utf-8")
    items = OutputParser.parse_json(content)
    assert len(items) == 2
    assert items[0]["template-id"] == "cve-2021-44228"

def test_trufflehog_fixture():
    content = (FIXTURES_DIR / "trufflehog.json").read_text(encoding="utf-8")
    items = OutputParser.parse_json(content)
    assert len(items) == 2
    assert items[0]["DetectorName"] == "AWS"
