from typer.testing import CliRunner
from cli.main import app
from unittest.mock import Mock, patch

runner = CliRunner()

@patch("cli.commands.scan_service")
def test_cli_scan(mock_scan_service):
    mock_scan_service.submit_scan.return_value = "job-123"
    mock_scan_service.get_status.side_effect = [
        {"status": "running", "progress": 50.0, "current_stage": "recon"},
        {"status": "completed", "progress": 100.0, "current_stage": "report"},
        {"status": "completed", "progress": 100.0, "current_stage": "report"}
    ]
    
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

@patch("cli.commands.scan_service")
def test_cli_scan_failed(mock_scan_service):
    mock_scan_service.submit_scan.return_value = "job-123"
    mock_scan_service.get_status.return_value = {
        "status": "failed",
        "error": "Timeout"
    }
    
    result = runner.invoke(app, ["scan", "example.com"])
    assert result.exit_code == 1
    assert "Scan failed:" in result.stdout

@patch("cli.commands.scan_service")
def test_cli_scan_validation_error(mock_scan_service):
    mock_scan_service.submit_scan.side_effect = ValueError("Bad domain")
    result = runner.invoke(app, ["scan", "example.com"])
    assert result.exit_code == 2
    assert "Validation Error:" in result.stdout

@patch("cli.commands.scan_service")
def test_cli_scan_generic_error(mock_scan_service):
    mock_scan_service.submit_scan.side_effect = RuntimeError("Bad")
    result = runner.invoke(app, ["scan", "example.com"])
    assert result.exit_code == 1
    assert "Error:" in result.stdout

import os
import json
import tempfile
@patch("cli.commands.scan_service")
def test_cli_scan_with_config(mock_scan_service):
    mock_scan_service.submit_scan.return_value = "job-123"
    mock_scan_service.get_status.return_value = None
    
    config_dict = {
        "settings": {"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        "llm": {"provider": "dummy", "default_model": "dummy", "timeout": 30},
        "tools": {"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        "timeouts": {"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        "reporting": {"report_formats": ["json"], "output_directories": {}}
    }
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(config_dict, f)
        f_name = f.name
        
    try:
        result = runner.invoke(app, ["scan", "example.com", "--config", f_name])
        assert result.exit_code == 0
    finally:
        os.unlink(f_name)

@patch("cli.commands.scan_service")
def test_cli_status_not_found(mock_scan_service):
    mock_scan_service.get_status.return_value = None
    result = runner.invoke(app, ["status", "job-123"])
    assert result.exit_code == 1
    assert "Job not found" in result.stdout

@patch("cli.commands.report_service")
def test_cli_report_not_found(mock_report_service):
    mock_report_service.get_report.return_value = None
    result = runner.invoke(app, ["report", "job-123"])
    assert result.exit_code == 1
    assert "Report not found" in result.stdout

@patch("cli.commands.scan_service")
def test_cli_cancel(mock_scan_service):
    mock_scan_service.cancel_scan.return_value = True
    result = runner.invoke(app, ["cancel", "job-123"])
    assert result.exit_code == 0
    assert "cancelled" in result.stdout
    
    mock_scan_service.cancel_scan.return_value = False
    result = runner.invoke(app, ["cancel", "job-123"])
    assert result.exit_code == 0
    assert "could not be cancelled" in result.stdout

from services.job_registry import JobStatus
class MockJob:
    def __init__(self):
        self.job_id = "job-1"
        self.target_domain = "example.com"
        self.status = JobStatus.RUNNING
        self.progress = 50.0

@patch("cli.commands.registry")
def test_cli_list_jobs(mock_registry):
    mock_registry.get_all_jobs.return_value = []
    result = runner.invoke(app, ["list-jobs"])
    assert result.exit_code == 0
    assert "No jobs found" in result.stdout
    
    mock_registry.get_all_jobs.return_value = [MockJob()]
    result = runner.invoke(app, ["list-jobs"])
    assert result.exit_code == 0
    assert "job-1" in result.stdout

def test_cli_validate_config():
    config_dict = {
        "settings": {"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        "llm": {"provider": "dummy", "default_model": "dummy", "timeout": 30},
        "tools": {"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        "timeouts": {"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        "reporting": {"report_formats": ["json"], "output_directories": {}}
    }
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        json.dump(config_dict, f)
        f_name = f.name
        
    try:
        result = runner.invoke(app, ["validate-config", f_name])
        assert result.exit_code == 0
        assert "valid" in result.stdout
    finally:
        os.unlink(f_name)
        
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
        f.write('{"settings": {"scan_depth": "invalid"}}')
        f.flush()
        f_name = f.name
        
    try:
        result = runner.invoke(app, ["validate-config", f_name])
        assert result.exit_code == 2
        assert "Invalid configuration" in result.stdout
    finally:
        os.unlink(f_name)

    result = runner.invoke(app, ["validate-config", "does_not_exist.json"])
    assert result.exit_code == 1
    assert "Unexpected Error" in result.stdout
