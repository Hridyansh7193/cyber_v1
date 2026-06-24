import pytest
from unittest.mock import patch, MagicMock
import subprocess
from execution.utils.process_runner import ProcessRunner
from execution.utils.timeout_manager import TimeoutManager

def test_process_runner_success():
    with patch("execution.utils.process_runner.subprocess.run") as mock_run:
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
    with patch("execution.utils.process_runner.subprocess.run", side_effect=subprocess.TimeoutExpired(["ls"], 300, b"partial out")):
        exit_code, stdout, stderr, ex_time = ProcessRunner.run(["ls"], "test_tool")

        assert exit_code == -1
        assert stdout == "partial out"
        assert "timed out" in stderr

def test_process_runner_oserror():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=OSError("No such file")):
        exit_code, stdout, stderr, ex_time = ProcessRunner.run(["ls"], "test_tool")
        assert exit_code == -2
        assert stdout == ""
        assert "No such file" in stderr

def test_process_runner_called_process_error():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=subprocess.CalledProcessError(127, ["ls"], b"out", b"err")):
        exit_code, stdout, stderr, ex_time = ProcessRunner.run(["ls"], "test_tool")
        assert exit_code == 127
        assert stdout == "out"
        assert stderr == "err"

def test_process_runner_programming_errors_propagate():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=TypeError("Bad type")):
        with pytest.raises(TypeError):
            ProcessRunner.run(["ls"], "test_tool")
            
    with patch("execution.utils.process_runner.subprocess.run", side_effect=KeyError("Bad key")):
        with pytest.raises(KeyError):
            ProcessRunner.run(["ls"], "test_tool")
            
    with patch("execution.utils.process_runner.subprocess.run", side_effect=ValueError("Bad value")):
        with pytest.raises(ValueError):
            ProcessRunner.run(["ls"], "test_tool")
            
    with patch("execution.utils.process_runner.subprocess.run", side_effect=AttributeError("Bad attr")):
        with pytest.raises(AttributeError):
            ProcessRunner.run(["ls"], "test_tool")

def test_timeout_manager_heavy_tool():
    assert TimeoutManager.get_timeout("nuclei") == TimeoutManager.HEAVY_TIMEOUT

def test_timeout_manager_default_tool():
    assert TimeoutManager.get_timeout("unknown_tool") == TimeoutManager.DEFAULT_TIMEOUT
