import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from cli.commands_report import app

runner = CliRunner()

@patch("cli.commands_report.persistence_service")
def test_report_cmd_not_found(mock_persistence):
    mock_persistence.get_session.return_value = None
    
    result = runner.invoke(app, ["report", "invalid-job"])
    assert result.exit_code == 1
    assert "not found in database" in result.stdout

@patch("cli.commands_report.persistence_service")
def test_report_cmd_success(mock_persistence):
    class DummySession:
        pass
    mock_persistence.get_session.return_value = DummySession()
    
    class DummyReport:
        id = "report-123"
        report_format = "markdown"
        created_at = "2026-06-29T12:00:00"
    mock_persistence.get_reports_for_session.return_value = [DummyReport()]
    
    result = runner.invoke(app, ["report", "job-123"])
    assert result.exit_code == 0
    assert "report-123" in result.stdout

@patch("cli.commands_report.workspace_service.workspace_manager")
@patch("cli.commands_report.persistence_service")
def test_export_cmd_success(mock_persistence, mock_manager):
    class DummySession:
        target_domain = "example.com"
    mock_persistence.get_session.return_value = DummySession()
    
    mock_manager.archive_session.return_value = "/path/to/export.zip"
    
    result = runner.invoke(app, ["export", "job-123"])
    assert result.exit_code == 0
    assert "Successfully exported" in result.stdout

@patch("cli.commands_report.workspace_service.workspace_manager")
@patch("cli.commands_report.persistence_service")
def test_inspect_cmd_success(mock_persistence, mock_manager):
    class DummySession:
        target_domain = "example.com"
        status = "completed"
    mock_persistence.get_session.return_value = DummySession()
    
    mock_persistence.get_findings_for_session.return_value = []
    mock_persistence.get_reports_for_session.return_value = []
    mock_persistence.get_logs_for_session.return_value = []
    
    mock_manager.get_session_dir.return_value.exists.return_value = True
    
    result = runner.invoke(app, ["inspect", "job-123"])
    assert result.exit_code == 0
    assert "Inspection for Job: job-123" in result.stdout
    assert "Findings: 0" in result.stdout
