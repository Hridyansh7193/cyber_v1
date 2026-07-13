import uuid
from services.report_service import ReportService
from schemas.report import Report, ReportFormat

def test_report_service_render_reports_json():
    report_service = ReportService()
    report = Report(
        report_id=uuid.uuid4(),
        session_id="job-123",
        report_format=ReportFormat.JSON,
    )
    
    generated = report_service.render_reports([report])
    assert len(generated) == 1
    assert generated[0].format == "json"
    assert "job-123" in generated[0].content
    assert generated[0].mime_type == "application/json"
    assert "report_" in generated[0].filename

def test_report_service_render_reports_markdown():
    report_service = ReportService()
    report = Report(
        report_id=uuid.uuid4(),
        session_id="job-123",
        report_format=ReportFormat.MARKDOWN,
    )
    
    generated = report_service.render_reports([report])
    assert len(generated) == 1
    assert generated[0].format == "markdown"
    assert "## Findings" in generated[0].content
    assert generated[0].mime_type == "text/markdown"
    assert "report_" in generated[0].filename
