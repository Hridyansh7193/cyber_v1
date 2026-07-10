import pytest
import uuid
from schemas.report import Report, DiscoveredAssets
from schemas.finding import Finding
from reporting.sarif_renderer import generate_sarif
from reporting.csv_renderer import generate_csv
from reporting.burpxml_renderer import generate_burpxml

def test_generate_sarif():
    rep = Report(
        findings=(
            Finding(title="Test Finding", severity="high", confidence="high", evidence="http://example.com"),
        ),
        assets=DiscoveredAssets()
    )
    result = generate_sarif(rep)
    assert result.format == "sarif"
    assert "Test Finding" in str(result.content)
    assert "example.com" in str(result.content)

def test_generate_csv():
    rep = Report(
        findings=(
            Finding(title="Test Finding CSV", severity="low", confidence="certain", evidence="payload", source_tool="nuclei"),
        ),
        assets=DiscoveredAssets()
    )
    result = generate_csv(rep)
    assert result.format == "csv"
    assert "Test Finding CSV" in str(result.content)
    assert "nuclei" in str(result.content)

def test_generate_burpxml():
    rep = Report(
        findings=(
            Finding(title="Test Finding XML", severity="critical", confidence="certain", evidence="details"),
        ),
        assets=DiscoveredAssets()
    )
    result = generate_burpxml(rep)
    assert result.format == "burpxml"
    assert "Test Finding XML" in str(result.content)
    assert "8388608" in str(result.content)
