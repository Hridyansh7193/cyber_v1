import pytest
from unittest.mock import patch, MagicMock
import subprocess
from execution.utils.process_runner import ProcessRunner
from execution.utils.timeout_manager import TimeoutManager

def test_process_runner_success():
    with patch("subprocess.run") as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "test output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        exit_code, stdout, stderr, ex_time = ProcessRunner.run(["ls"], "test_tool")

        assert exit_code == 0
        assert stdout == "test output"
        assert stderr == ""
        assert ex_time >= 0

def test_process_runner_timeout():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["ls"], 300, b"partial out")):
        exit_code, stdout, stderr, ex_time = ProcessRunner.run(["ls"], "test_tool")

        assert exit_code == -1
        assert stdout == "partial out"
        assert "timed out" in stderr

def test_process_runner_exception():
    with patch("subprocess.run", side_effect=FileNotFoundError("No such file")):
        exit_code, stdout, stderr, ex_time = ProcessRunner.run(["ls"], "test_tool")

        assert exit_code == -2
        assert stdout == ""
        assert "No such file" in stderr

def test_timeout_manager_heavy_tool():
    assert TimeoutManager.get_timeout("nuclei") == TimeoutManager.HEAVY_TIMEOUT

def test_timeout_manager_default_tool():
    assert TimeoutManager.get_timeout("unknown_tool") == TimeoutManager.DEFAULT_TIMEOUT
