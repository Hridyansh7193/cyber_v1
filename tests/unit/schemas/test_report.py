import pytest
from datetime import datetime
from pydantic import ValidationError
from schemas.report import Report, ReportFormat

def test_report_valid():
    now = datetime.now()
    report = Report(
        session_id="session123",
        report_path="/tmp/report.json",
        report_format=ReportFormat.JSON,
        timestamp=now
    )
    assert report.session_id == "session123"
    assert report.report_path == "/tmp/report.json"
    assert report.report_format == ReportFormat.JSON
    assert report.timestamp == now

def test_report_invalid_format():
    now = datetime.now()
    with pytest.raises(ValidationError):
        Report(
            session_id="123",
            report_path="/tmp/report.txt",
            report_format="txt",
            timestamp=now
        )
