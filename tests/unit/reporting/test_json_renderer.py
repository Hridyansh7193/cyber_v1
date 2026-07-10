import json
from uuid import uuid4
from datetime import datetime, timezone
from schemas.report import Report
from schemas.finding import Finding, Severity, Confidence
from reporting.json_renderer import generate_json

def test_json_renderer_basic():
    report_id = uuid4()
    report = Report(
        report_id=report_id,
        created_at=datetime.now(timezone.utc),
        findings=[
            Finding(title="SQLi", severity=Severity.CRITICAL, confidence=Confidence.CERTAIN, evidence="' OR 1=1")
        ],
        total_findings=1
    )
    
    
    before = report.model_dump()
    generated = generate_json(report)
    after = report.model_dump()
    
    assert before == after
    
    assert generated.format == "json"
    assert f"report_{report_id}.json" == generated.filename
    assert generated.mime_type == "application/json"
    assert generated.encoding == "utf-8"
    assert not generated.is_binary
    
    parsed = json.loads(generated.content)
    assert parsed["report_id"] == str(report_id)
    assert parsed["total_findings"] == 1
    assert parsed["findings"][0]["title"] == "SQLi"

def test_json_renderer_huge_nested():
    findings = [
        Finding(title=f"Finding {i}", severity=Severity.LOW, confidence=Confidence.MEDIUM, evidence="Ev")
        for i in range(1000)
    ]
    report = Report(
        report_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        findings=findings,
        total_findings=1000
    )
    generated = generate_json(report)
    parsed = json.loads(generated.content)
    assert len(parsed["findings"]) == 1000
    assert parsed["findings"][999]["title"] == "Finding 999"
