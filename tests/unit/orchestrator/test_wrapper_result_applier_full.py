import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from schemas.tool_result import ToolResult
from orchestrator.wrapper_result_applier import (
    apply_recon_wrapper_result, apply_js_wrapper_result, 
    apply_api_wrapper_result, apply_vuln_wrapper_result
)

def get_base_state():
    return ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))

def get_tool_result(metadata):
    return ToolResult(tool_name="test", metadata=metadata, success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)

def test_apply_recon_wrapper():
    state = get_base_state()
    res = apply_recon_wrapper_result(state, get_tool_result({"new_subdomains": ["sub1"], "new_hosts": ["h1"], "new_urls": ["u1"]}))
    assert res is not state
    assert "sub1" in res.recon_state.subdomains
    assert "h1" in res.recon_state.alive_hosts
    assert "u1" in res.recon_state.urls

def test_apply_js_wrapper():
    state = get_base_state()
    res = apply_js_wrapper_result(state, get_tool_result({"new_js_files": ["js1"], "new_endpoints": ["e1"]}))
    assert res is not state
    assert "js1" in res.js_state.js_files
    assert "e1" in res.js_state.endpoints

def test_apply_api_wrapper():
    state = get_base_state()
    res = apply_api_wrapper_result(state, get_tool_result({"new_swagger": ["s1"], "new_graphql": ["g1"]}))
    assert res is not state
    assert "s1" in res.api_state.swagger_urls
    assert "g1" in res.api_state.graphql_urls

def test_apply_vuln_wrapper():
    state = get_base_state()
    res = apply_vuln_wrapper_result(state, get_tool_result({"new_nuclei": [{"id": "vuln1"}], "new_dalfox": [{"id": "vuln2"}]}))
    assert res is not state
    assert len(res.vuln_state.nuclei_results) == 1
    assert len(res.vuln_state.dalfox_results) == 1
