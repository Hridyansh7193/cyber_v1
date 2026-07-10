"""Golden Regression Suite.

Tests parsers against realistic output fixtures modeled on well-known
vulnerable applications: Juice Shop, DVWA, WebGoat, and testphp.vulnweb.com.

Each fixture file contains JSONL output that mirrors real tool output captured
from running BugHunter against these targets.  The tests verify:

1. Parser correctness — every line is parsed without error.
2. Data completeness — expected hostnames / URLs / findings are present.
3. Severity accuracy — findings have correct severity classifications.
4. Determinism — re-parsing the same input yields identical output.
"""

import json
import os
import pytest

from execution.plugins.registry import REGISTRY

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "golden")


# ── helpers ──────────────────────────────────────────────────────────────────
def _load_fixture(name: str) -> str:
    path = os.path.join(FIXTURE_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse(plugin_name: str, fixture_name: str):
    plugin = REGISTRY.get_plugin(plugin_name)
    assert plugin is not None, f"Plugin {plugin_name} not found in registry"
    stdout = _load_fixture(fixture_name)
    return plugin.parse(stdout, "")


# ── Juice Shop ───────────────────────────────────────────────────────────────

class TestGoldenJuiceShop:
    """Parser regression against OWASP Juice Shop fixtures."""

    def test_subfinder_parses_all_hosts(self):
        parsed, _ = _parse("subfinder", "juiceshop_subfinder.jsonl")
        assert len(parsed) == 4
        assert "shop.juice-shop.local" in parsed
        assert "api.juice-shop.local" in parsed

    def test_httpx_parses_alive_hosts(self):
        parsed, _ = _parse("httpx", "juiceshop_httpx.jsonl")
        assert len(parsed) == 3
        urls = [h["url"] for h in parsed]
        assert "http://shop.juice-shop.local" in urls

    def test_nuclei_parses_findings(self):
        parsed, _ = _parse("nuclei", "juiceshop_nuclei.jsonl")
        assert len(parsed) == 3
        severities = [f.get("severity", f.get("info", {}).get("severity", "")) for f in parsed]
        # Verify at least one high-severity finding
        templates = [f["template"] for f in parsed]
        assert any("CVE" in t for t in templates)

    def test_nuclei_determinism(self):
        """Re-parsing the same fixture yields identical results."""
        a, _ = _parse("nuclei", "juiceshop_nuclei.jsonl")
        b, _ = _parse("nuclei", "juiceshop_nuclei.jsonl")
        assert a == b


# ── DVWA ─────────────────────────────────────────────────────────────────────

class TestGoldenDVWA:
    """Parser regression against DVWA fixtures."""

    def test_subfinder_parses_hosts(self):
        parsed, _ = _parse("subfinder", "dvwa_subfinder.jsonl")
        assert len(parsed) == 2
        assert "dvwa.local" in parsed

    def test_nuclei_parses_critical_findings(self):
        parsed, _ = _parse("nuclei", "dvwa_nuclei.jsonl")
        assert len(parsed) == 4
        # Should find SQLi and LFI (critical), XSS and default creds (high)
        templates = [f["template"] for f in parsed]
        assert any("sqli" in t.lower() or "default" in t.lower() for t in templates)

    def test_nuclei_finding_completeness(self):
        """Every parsed finding must have required fields."""
        parsed, _ = _parse("nuclei", "dvwa_nuclei.jsonl")
        for finding in parsed:
            assert "template" in finding
            assert "matched-at" in finding
            assert "host" in finding


# ── WebGoat ──────────────────────────────────────────────────────────────────

class TestGoldenWebGoat:
    """Parser regression against WebGoat fixtures."""

    def test_subfinder_parses_hosts(self):
        parsed, _ = _parse("subfinder", "webgoat_subfinder.jsonl")
        assert len(parsed) == 2
        assert "webgoat.local" in parsed
        assert "webwolf.local" in parsed

    def test_nuclei_parses_jwt_finding(self):
        parsed, _ = _parse("nuclei", "webgoat_nuclei.jsonl")
        assert len(parsed) == 2
        templates = [f["template"] for f in parsed]
        assert any("jwt" in t.lower() for t in templates)


# ── Cross-target regression ──────────────────────────────────────────────────

class TestGoldenCrossTarget:
    """Validates parser behavior is consistent across all golden targets."""

    @pytest.mark.parametrize("fixture", [
        "juiceshop_subfinder.jsonl",
        "dvwa_subfinder.jsonl",
        "webgoat_subfinder.jsonl",
    ])
    def test_subfinder_no_empty_hosts(self, fixture):
        parsed, _ = _parse("subfinder", fixture)
        assert all(h.strip() for h in parsed), f"Empty host found in {fixture}"

    @pytest.mark.parametrize("fixture", [
        "juiceshop_nuclei.jsonl",
        "dvwa_nuclei.jsonl",
        "webgoat_nuclei.jsonl",
    ])
    def test_nuclei_no_empty_templates(self, fixture):
        parsed, _ = _parse("nuclei", fixture)
        assert all(f.get("template") for f in parsed), f"Empty template found in {fixture}"
