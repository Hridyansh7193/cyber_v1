import pytest
from pydantic import ValidationError
from datetime import datetime, UTC
from schemas.state import ExecutionState, ReconState, TargetState
from schemas.tool_result import ToolResult
from schemas.finding import Finding, Severity, Confidence
from schemas.report import Report, ReportFormat

def test_deep_nested_immutability():
    target = TargetState(domain="example.com", session_id="123", start_time=datetime.now(UTC))
    state = ExecutionState(target=target)

    # 1. state.recon_state.subdomains += ("x",) fails
    with pytest.raises(ValidationError):
        state.recon_state.subdomains += ("x",)
        
    # 2. state.findings.append(...) fails
    with pytest.raises(AttributeError):
        state.findings.append(Finding(title="x", severity=Severity.LOW, confidence=Confidence.LOW, evidence="x"))

    # 3. tool_result.metadata["key"] = "value" fails
    tool_result = ToolResult(tool_name="test", success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)
    with pytest.raises(TypeError):
        tool_result.metadata["key"] = "value"

    # 4. finding.evidence.append(...) fails
    finding = Finding(title="test", severity=Severity.LOW, confidence=Confidence.LOW, evidence="x")
    with pytest.raises(AttributeError):
        finding.evidence.append("new_evidence")

def test_model_copy_deep_compatibility():
    target = TargetState(domain="example.com", session_id="123", start_time=datetime.now(UTC))
    state = ExecutionState(target=target)
    
    new_recon = state.recon_state.model_copy(update={"subdomains": ("new.example.com",)})
    new_state = state.model_copy(deep=True, update={"recon_state": new_recon})
    
    assert new_state.recon_state.subdomains == ("new.example.com",)
    assert id(state) != id(new_state)
