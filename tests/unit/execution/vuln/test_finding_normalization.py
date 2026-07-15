from orchestrator.wrapper_result_applier import apply_vuln_wrapper_result
from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.tool_result import ToolResult
from datetime import datetime, timezone


def test_nuclei_classification_parsed():
    t_state = TargetState(domain="test.com", session_id="abc", start_time=datetime.now(timezone.utc))
    state = ExecutionState(target=t_state)

    metadata = {
        "new_nuclei": [
            {
                "template-id": "test-vuln",
                "info": {
                    "name": "Test Vuln",
                    "description": "Test description.",
                    "severity": "high",
                    "classification": {
                        "cve-id": ["CVE-2023-1234"],
                        "cwe-id": ["CWE-79"],
                        "cvss-metrics": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                        "cvss-score": 9.8
                    }
                },
                "host": "test.com",
                "matched-at": "http://test.com"
            }
        ]
    }

    tool_res = ToolResult(
        tool_name="nuclei",
        command="nuclei",
        success=True,
        exit_code=0,
        stdout="",
        stderr="",
        execution_time=1.5,
        metadata=metadata
    )

    new_state = apply_vuln_wrapper_result(state, (tool_res,))

    assert len(new_state.findings) == 1
    f = new_state.findings[0]
    assert f.title == "Test Vuln"
    assert f.description == "Test description."
    assert "CVE-2023-1234" in f.cve_ids
    assert "CWE-79" in f.cwe_ids
    assert f.cvss_score == 9.8
    assert f.cvss_vector == "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"


def test_swagger_api_recommendation():
    from utils.recommendations import get_recommendation

    vuln = {"template-id": "swagger-api"}
    rec = get_recommendation("swagger-api", "category", vuln)

    assert "Restrict production documentation exposure" in rec
