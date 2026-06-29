import pytest
from unittest.mock import patch
from typer.testing import CliRunner
from cli.commands_workspace import app

runner = CliRunner()

@patch("cli.commands_workspace.persistence_service")
def test_workspace_list_no_sessions(mock_persistence):
    mock_persistence.get_all_sessions.return_value = []
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No sessions found" in result.stdout

@patch("cli.commands_workspace.persistence_service")
def test_workspace_list_with_sessions(mock_persistence):
    class DummySession:
        session_id = "test-job-123"
        target_domain = "example.com"
        status = "completed"
        started_at = "2026-06-29T12:00:00"
    mock_persistence.get_all_sessions.return_value = [DummySession()]
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "test-job-123" in result.stdout
    assert "example.com" in result.stdout

@patch("cli.commands_workspace.workspace_service.workspace_manager")
def test_workspace_stats(mock_manager):
    mock_manager.get_workspace_stats.return_value = {
        "targets": 2,
        "sessions": 5,
        "reports": 10,
        "logs": 20,
        "total_size_bytes": 1048576 * 5 # 5 MB
    }
    
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0
    assert "Targets" in result.stdout
    assert "5.00 MB" in result.stdout

@patch("cli.commands_workspace.persistence_service")
def test_workspace_browse_not_found(mock_persistence):
    mock_persistence.get_session.return_value = None
    
    result = runner.invoke(app, ["browse", "invalid-job"])
    assert result.exit_code == 1
    assert "not found in database" in result.stdout

@patch("cli.commands_workspace.workspace_service.workspace_manager")
@patch("cli.commands_workspace.persistence_service")
def test_workspace_archive_success(mock_persistence, mock_manager):
    class DummySession:
        target_domain = "example.com"
    mock_persistence.get_session.return_value = DummySession()
    
    mock_manager.archive_session.return_value = "/path/to/archive.zip"
    
    result = runner.invoke(app, ["archive", "job-123"])
    assert result.exit_code == 0
    assert "Successfully archived" in result.stdout

@patch("cli.commands_workspace.workspace_service.workspace_manager")
def test_workspace_clean_success(mock_manager):
    result = runner.invoke(app, ["clean"])
    assert result.exit_code == 0
    assert "Successfully cleaned" in result.stdout
    mock_manager.clean_temp.assert_called_once()
