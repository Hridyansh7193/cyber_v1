import pytest
from pydantic import ValidationError
from schemas.tool_result import ToolResult

def test_tool_result_defaults():
    tr = ToolResult(
        tool_name="nmap",
        success=True,
        exit_code=0,
        stdout="done",
        stderr="",
        execution_time=1.5
    )
    assert tr.success is True
    assert tr.tool_name == "nmap"
    assert tr.exit_code == 0
    assert tr.stdout == "done"
    assert tr.execution_time == 1.5
    assert tr.raw_output_path is None
    assert tr.metadata == {}

def test_tool_result_custom():
    tr = ToolResult(
        tool_name="subfinder",
        success=False,
        exit_code=1,
        stdout="",
        stderr="error",
        execution_time=5.0,
        raw_output_path="/tmp/out",
        metadata={"version": "1.0"}
    )
    assert tr.success is False
    assert tr.exit_code == 1
    assert tr.stderr == "error"
    assert tr.raw_output_path == "/tmp/out"

def test_tool_result_invalid_time():
    with pytest.raises(ValidationError):
        ToolResult(
            tool_name="nmap",
            success=True,
            exit_code=0,
            stdout="done",
            stderr="",
            execution_time=-1.0
        )
