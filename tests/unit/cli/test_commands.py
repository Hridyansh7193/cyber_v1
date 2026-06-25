from typer.testing import CliRunner
from cli.main import app
from unittest.mock import Mock, patch

runner = CliRunner()

@patch("cli.commands.scan_service")
def test_cli_scan(mock_scan_service):
    mock_scan_service.submit_scan.return_value = "job-123"
    mock_scan_service.get_status.return_value = {
        "status": "completed",
        "progress": 100.0,
        "current_stage": "report"
    }
    
    result = runner.invoke(app, ["scan", "example.com"])
    assert result.exit_code == 0
    assert "Scan submitted!" in result.stdout
    assert "job-123" in result.stdout

@patch("cli.commands.scan_service")
def test_cli_status(mock_scan_service):
    mock_scan_service.get_status.return_value = {
        "job_id": "job-123",
        "target": "example.com",
        "status": "running",
        "progress": 50.0,
        "current_stage": "recon",
        "started_at": "2023-01-01T00:00:00Z",
        "completed_at": None,
        "error": None
    }
    
    result = runner.invoke(app, ["status", "job-123"])
    assert result.exit_code == 0
    assert "Status for job-123" in result.stdout
    assert "running" in result.stdout

@patch("cli.commands.report_service")
def test_cli_report(mock_report_service):
    mock_report = Mock()
    mock_report.content = "report_content_here"
    mock_report_service.get_report.return_value = mock_report
    
    result = runner.invoke(app, ["report", "job-123"])
    assert result.exit_code == 0
    assert "report_content_here" in result.stdout

def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "BugHunter v0.1.0" in result.stdout
