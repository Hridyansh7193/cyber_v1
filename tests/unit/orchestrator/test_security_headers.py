from orchestrator.wrapper_result_applier import apply_vuln_wrapper_result
from schemas.state import ExecutionState, ReconState, TargetState
from schemas.tool_result import ToolResult

def test_missing_security_headers_logic():
    from datetime import datetime, timezone
    state = ExecutionState(
        target=TargetState(domain="example.com", session_id="123", start_time=datetime.now(timezone.utc)),
        recon_state=ReconState(urls=("http://localhost:3000", "https://example.com"))
    )
    
    # 1. NOT_MEASURED (no extracted-results) -> drops finding
    tr1 = ToolResult(
        tool_name="nuclei",
        success=True,
        execution_time=1.0,
        exit_code=0, stdout="", stderr="",
        metadata={
            "new_nuclei": [
                {
                    "template-id": "missing-security-headers",
                    "matched-at": "https://example.com",
                    "host": "example.com"
                }
            ]
        }
    )
    new_state = apply_vuln_wrapper_result(state, (tr1,))
    assert len(new_state.findings) == 0, "Should drop finding if no reliable evidence exists"
    
    # 2. HTTP localhost target, HSTS removed -> drops finding if no other headers missing
    tr2 = ToolResult(
        tool_name="nuclei",
        success=True,
        execution_time=1.0,
        exit_code=0, stdout="", stderr="",
        metadata={
            "new_nuclei": [
                {
                    "template-id": "missing-security-headers",
                    "matched-at": "http://localhost:3000",
                    "host": "localhost:3000",
                    "extracted-results": ["Strict-Transport-Security"]
                }
            ]
        }
    )
    new_state2 = apply_vuln_wrapper_result(state, (tr2,))
    assert len(new_state2.findings) == 0, "Should drop HSTS on HTTP localhost"
    
    # 3. HTTP localhost target, HSTS removed but other header missing -> keeps finding
    tr3 = ToolResult(
        tool_name="nuclei",
        success=True,
        execution_time=1.0,
        exit_code=0, stdout="", stderr="",
        metadata={
            "new_nuclei": [
                {
                    "template-id": "missing-security-headers",
                    "matched-at": "http://localhost:3000",
                    "host": "localhost:3000",
                    "extracted-results": ["Strict-Transport-Security", "X-Frame-Options"]
                }
            ]
        }
    )
    new_state3 = apply_vuln_wrapper_result(state, (tr3,))
    assert len(new_state3.findings) == 1
    assert "X-Frame-Options" in new_state3.findings[0].evidence
    assert "Strict-Transport-Security" not in new_state3.findings[0].evidence
    
    # 4. HTTPS target -> keeps HSTS
    tr4 = ToolResult(
        tool_name="nuclei",
        success=True,
        execution_time=1.0,
        exit_code=0, stdout="", stderr="",
        metadata={
            "new_nuclei": [
                {
                    "template-id": "missing-security-headers",
                    "matched-at": "https://example.com",
                    "host": "example.com",
                    "extracted-results": ["Strict-Transport-Security", "X-Frame-Options"]
                }
            ]
        }
    )
    new_state4 = apply_vuln_wrapper_result(state, (tr4,))
    assert len(new_state4.findings) == 1
    assert "Strict-Transport-Security" in new_state4.findings[0].evidence
