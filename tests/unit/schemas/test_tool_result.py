import pytest
from pydantic import ValidationError
from schemas.tool_result import ToolResult

def test_tool_result_defaults():
    tr = ToolResult(success=True, tool_name="nmap", execution_time=1.5)
    assert tr.success is True
    assert tr.tool_name == "nmap"
    assert tr.execution_time == 1.5
    assert tr.raw_output_path is None
    assert tr.structured_output == {}
    assert tr.errors == []
    assert tr.metadata == {}

def test_tool_result_custom():
    tr = ToolResult(
        success=False,
        tool_name="subfinder",
        execution_time=5.0,
        raw_output_path="/tmp/out",
        structured_output={"subdomains": ["a.com"]},
        errors=["Timeout"],
        metadata={"version": "1.0"}
    )
    assert tr.success is False
    assert tr.raw_output_path == "/tmp/out"
    assert tr.structured_output == {"subdomains": ["a.com"]}
    assert tr.errors == ["Timeout"]

def test_tool_result_invalid_time():
    with pytest.raises(ValidationError):
        ToolResult(success=True, tool_name="nmap", execution_time=-1.0)
