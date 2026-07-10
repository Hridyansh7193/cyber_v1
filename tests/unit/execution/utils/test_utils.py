from execution.utils.process_runner import ProcessRunner
from execution.utils.timeout_manager import TimeoutManager
from unittest.mock import patch, MagicMock
import subprocess

def test_process_runner_success():
    with patch("execution.utils.process_runner.subprocess.run") as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "test output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        res = ProcessRunner.run(["ls"], "test_tool")

        assert res.exit_code == 0
        assert res.stdout == "test output"
        assert res.stderr == ""
        assert res.execution_time >= 0

def test_process_runner_timeout():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=subprocess.TimeoutExpired(["ls"], 300, b"partial out")):
        res = ProcessRunner.run(["ls"], "test_tool")

        assert res.exit_code == -1
        assert res.stdout == "partial out"
        assert "timed out" in res.stderr

def test_process_runner_oserror():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=OSError("No such file")):
        res = ProcessRunner.run(["ls"], "test_tool")
        assert res.exit_code == -2
        assert res.stdout == ""
        assert "No such file" in res.stderr

def test_process_runner_called_process_error():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=subprocess.CalledProcessError(127, ["ls"], b"out", b"err")):
        res = ProcessRunner.run(["ls"], "test_tool")
        assert res.exit_code == 127
        assert res.stdout == "out"
        assert res.stderr == "err"

def test_process_runner_programming_errors_propagate():
    with patch("execution.utils.process_runner.subprocess.run", side_effect=TypeError("Bad type")):
        result = ProcessRunner.run(["ls"], "test_tool")
        assert result.exit_code == -2
        assert "Execution error" in result.error_message
            
    with patch("execution.utils.process_runner.subprocess.run", side_effect=KeyError("Bad key")):
        result = ProcessRunner.run(["ls"], "test_tool")
        assert result.exit_code == -2
            
    with patch("execution.utils.process_runner.subprocess.run", side_effect=ValueError("Bad value")):
        result = ProcessRunner.run(["ls"], "test_tool")
        assert result.exit_code == -2
            
    with patch("execution.utils.process_runner.subprocess.run", side_effect=AttributeError("Bad attr")):
        result = ProcessRunner.run(["ls"], "test_tool")
        assert result.exit_code == -2

def test_timeout_manager_heavy_tool():
    assert TimeoutManager.get_timeout("nuclei") == TimeoutManager.HEAVY_TIMEOUT

def test_timeout_manager_default_tool():
    assert TimeoutManager.get_timeout("unknown_tool") == TimeoutManager.DEFAULT_TIMEOUT
