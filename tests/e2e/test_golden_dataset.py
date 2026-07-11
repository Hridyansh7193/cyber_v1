from execution.plugins.registry import REGISTRY
import json

def test_golden_dataset_subfinder():
    plugin = REGISTRY.get_plugin("subfinder")
    stdout = '{"host": "sub1.example.com"}\n{"host": "sub2.example.com"}\n'
    parsed, _ = plugin.parse(stdout, "")
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert "sub1.example.com" in parsed
    assert "sub2.example.com" in parsed

def test_golden_dataset_nuclei():
    plugin = REGISTRY.get_plugin("nuclei")
    mock_json1 = json.dumps({
        "template": "test-template",
        "type": "http",
        "matched-at": "http://example.com"
    })
    mock_json2 = json.dumps({
        "template": "test-template-2",
        "type": "http",
        "matched-at": "http://test.com"
    })
    stdout = f"{mock_json1}\n{mock_json2}\n"
    parsed, _ = plugin.parse(stdout, "")
    assert len(parsed) == 2
    assert parsed[0]["template"] == "test-template"
    assert parsed[1]["matched-at"] == "http://test.com"

def test_golden_dataset_httpx():
    plugin = REGISTRY.get_plugin("httpx")
    mock_json = json.dumps({
        "url": "http://example.com",
        "status_code": 200,
        "title": "Example Domain"
    })
    stdout = f"{mock_json}\n"
    parsed, _ = plugin.parse(stdout, "")
    assert len(parsed) == 1
    assert parsed[0]["url"] == "http://example.com"
    assert parsed[0]["status_code"] == 200

def test_golden_dataset_dalfox():
    plugin = REGISTRY.get_plugin("dalfox")
    mock_json = json.dumps({
        "type": "XSS",
        "poc": "http://example.com/?q=<script>alert(1)</script>"
    })
    stdout = f"{mock_json}\n"
    parsed, _ = plugin.parse(stdout, "")
    assert len(parsed) == 1
    assert parsed[0]["type"] == "XSS"


def test_golden_dataset_dalfox_json_array():
    plugin = REGISTRY.get_plugin("dalfox")
    stdout = json.dumps([
        {"type": "XSS", "poc": "https://example.com/?q=one"},
        {"type": "XSS", "poc": "https://example.com/?q=two"},
    ], indent=2)

    parsed, errors = plugin.parse(stdout, "")

    assert errors == []
    assert [record["poc"] for record in parsed] == [
        "https://example.com/?q=one",
        "https://example.com/?q=two",
    ]

def test_golden_dataset_trufflehog():
    plugin = REGISTRY.get_plugin("trufflehog")
    mock_json = json.dumps({
        "SourceMetadata": {
            "Data": {"URL": "http://example.com/main.js"}
        },
        "DetectorName": "AWS",
        "Raw": "AKIAIOSFODNN7EXAMPLE"
    })
    stdout = f"{mock_json}\n"
    parsed, _ = plugin.parse(stdout, "")
    assert len(parsed) == 1
    assert parsed[0]["DetectorName"] == "AWS"
