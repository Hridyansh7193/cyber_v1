import pytest
from pydantic import ValidationError
from schemas.finding import Finding, Severity, Confidence

def test_finding_valid():
    finding = Finding(
        title="SQL Injection",
        severity=Severity.CRITICAL,
        confidence=Confidence.CERTAIN,
        evidence="Found via param check"
    )
    assert finding.title == "SQL Injection"
    assert finding.severity == Severity.CRITICAL
    assert finding.confidence == Confidence.CERTAIN
    assert finding.evidence == "Found via param check"
    assert finding.references == ()

def test_finding_with_references():
    finding = Finding(
        title="XSS",
        severity=Severity.HIGH,
        confidence=Confidence.HIGH,
        evidence="Alert popup",
        references=["http://cwe.mitre.org/data/definitions/79.html"]
    )
    assert finding.references == ("http://cwe.mitre.org/data/definitions/79.html",)

def test_finding_missing_required():
    with pytest.raises(ValidationError):
        Finding(title="XSS")

def test_finding_invalid_enum():
    with pytest.raises(ValidationError):
        Finding(title="XSS", severity="mega_high", confidence=Confidence.HIGH, evidence="none")
