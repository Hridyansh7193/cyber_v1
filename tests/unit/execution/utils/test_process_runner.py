import sys
import os
from unittest.mock import patch
from execution.utils.process_runner import ProcessRunner
from execution.utils.executable_resolver import ExecutableResolution, ResolutionSource, IdentityState

DUMMY_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "fixtures", "dummy_tool.py")

def mock_resolver(tool_name, config_path=None):
    # Always resolve the python executable so we can run our dummy script
    if tool_name == "python":
        return ExecutableResolution(
            tool_name="python",
            requested_path=None,
            resolved_path=sys.executable,
            source=ResolutionSource.SYSTEM_PATH,
            platform="Mock",
            exists=True,
            executable=True,
            identity_state=IdentityState.RESOLVED,
            error_code=0,
            error_message=""
        )
    return ExecutableResolution(
        tool_name=tool_name,
        requested_path=None,
        resolved_path=None,
        source=ResolutionSource.NOT_FOUND,
        platform="Mock",
        exists=False,
        executable=False,
        identity_state=IdentityState.MISSING,
        error_code=-2,
        error_message="Not found"
    )

@patch("execution.utils.process_runner.resolve_executable", side_effect=mock_resolver)
def test_process_runner_normal_exit(mock_resolve):
    result = ProcessRunner.run(["python", DUMMY_SCRIPT, "normal"], "dummy", timeout=5)
    assert result.exit_code == 0
    assert result.success is True
    assert "stdout line 1" in result.stdout
    assert "stderr line 1" in result.stderr
    assert result.execution_time > 0

@patch("execution.utils.process_runner.resolve_executable", side_effect=mock_resolver)
def test_process_runner_error_exit(mock_resolve):
    result = ProcessRunner.run(["python", DUMMY_SCRIPT, "error"], "dummy", timeout=5)
    assert result.exit_code == 42
    assert result.success is False

@patch("execution.utils.process_runner.resolve_executable", side_effect=mock_resolver)
def test_process_runner_timeout_preserves_partial_output(mock_resolve):
    result = ProcessRunner.run(["python", DUMMY_SCRIPT, "timeout"], "dummy", timeout=1)
    assert result.exit_code == -1
    assert result.success is False
    assert "stdout before timeout" in result.stdout
    assert "stderr before timeout" in result.stderr
    assert "stdout after timeout" not in result.stdout
    assert "Process timed out" in result.error_message

@patch("execution.utils.process_runner.resolve_executable", side_effect=mock_resolver)
def test_process_runner_missing_binary(mock_resolve):
    result = ProcessRunner.run(["missing_binary"], "dummy", timeout=5)
    assert result.exit_code == -3
    assert result.success is False
    assert "not found or not executable" in result.error_message

@patch("execution.utils.process_runner.resolve_executable", side_effect=mock_resolver)
def test_process_runner_crash(mock_resolve):
    result = ProcessRunner.run(["python", DUMMY_SCRIPT, "crash"], "dummy", timeout=5)
    # The python script will exit with 1 due to the uncaught exception
    assert result.exit_code == 1
    assert result.success is False
    assert "Fatal crash" in result.stderr
