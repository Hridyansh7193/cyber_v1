from uuid import uuid4
from datetime import datetime, timezone
from schemas.report import Report
from schemas.finding import Finding, Severity, Confidence
from reporting.markdown_renderer import generate_markdown
from storage.file_storage import save_generated_file

def test_reporting_e2e_markdown(tmp_path):
    # 1. Create Report
    report = Report(
        report_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        findings=[
            Finding(title="E2E Test", severity=Severity.MEDIUM, confidence=Confidence.MEDIUM, evidence="evidence")
        ],
        total_findings=1
    )
    
    # 2. Render to GeneratedReport
    generated = generate_markdown(report)
    
    # 3. Save to storage
    saved_path = save_generated_file(generated, tmp_path)
    
    # 4. Read back and verify
    assert saved_path.exists()
    content = saved_path.read_text(encoding="utf-8")
    
    assert str(report.report_id) in content

def test_reporting_stress_10000_findings(tmp_path):
    findings = [
        Finding(title=f"Finding {i}", severity=Severity.LOW, confidence=Confidence.MEDIUM, evidence="Ev")
        for i in range(10000)
    ]
    report = Report(
        report_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        findings=findings,
        total_findings=10000
    )
    
    # Markdown
    md_generated = generate_markdown(report)
    md_path = save_generated_file(md_generated, tmp_path)
    assert md_path.exists()
    
    # JSON
    from reporting.json_renderer import generate_json
    json_generated = generate_json(report)
    json_path = save_generated_file(json_generated, tmp_path)
    assert json_path.exists()

