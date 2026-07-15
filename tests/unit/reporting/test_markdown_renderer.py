from uuid import uuid4
from datetime import datetime, timezone
from schemas.report import Report
from schemas.finding import Finding, Severity, Confidence
from reporting.markdown_renderer import generate_markdown

def test_markdown_renderer_basic():
    report = Report(
        report_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        findings=[
            Finding(title="XSS", severity=Severity.HIGH, confidence=Confidence.CERTAIN, evidence="<script>")
        ],
        total_findings=1
    )
    
    
    before = report.model_dump()
    generated = generate_markdown(report)
    after = report.model_dump()
    
    assert before == after
    
    assert generated.format == "markdown"
    assert generated.filename == "report.md"
    assert generated.mime_type == "text/markdown"
    assert generated.encoding == "utf-8"
    assert not generated.is_binary
    assert "BugHunter-Agent Report" in generated.content
    assert "XSS" in generated.content

def test_markdown_renderer_unicode():
    report = Report(
        report_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        findings=[
            Finding(title="नमस्ते", severity=Severity.INFO, confidence=Confidence.LOW, evidence="🚀\n测试")
        ],
        total_findings=1
    )
    generated = generate_markdown(report)
    assert "नमस्ते" in generated.content
    assert "测试" in generated.content
    assert "🚀" in generated.content

def test_markdown_renderer_empty():
    report = Report(
        report_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        findings=[],
        total_findings=0
    )
    generated = generate_markdown(report)
    assert "## Executive Summary" in generated.content

def test_markdown_renderer_huge():
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
    generated = generate_markdown(report)
    assert "Finding 999" in generated.content
