import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.delta_applier import (
    apply_recon_delta, apply_js_delta, apply_api_delta, 
    apply_vulnerability_delta, apply_analysis_delta, apply_report_delta
)
from agents.deltas import ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, AnalysisDelta, ReportDelta

def get_base_state():
    return ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))

def test_apply_recon_delta():
    state = get_base_state()
    delta = ReconDelta(subdomains=("sub1",), alive_hosts=("h1",), urls=("u1",))
    new_state = apply_recon_delta(state, delta)
    assert new_state is not state
    assert "sub1" in new_state.recon_state.subdomains

def test_apply_js_delta():
    state = get_base_state()
    delta = JSDelta(js_files=("f1",), endpoints=("e1",))
    new_state = apply_js_delta(state, delta)
    assert new_state is not state
    assert "f1" in new_state.js_state.js_files

def test_apply_api_delta():
    state = get_base_state()
    delta = APIDelta(swagger_urls=("s1",), graphql_urls=("g1",))
    new_state = apply_api_delta(state, delta)
    assert new_state is not state
    assert "s1" in new_state.api_state.swagger_urls

def test_apply_vulnerability_delta():
    state = get_base_state()
    delta = VulnerabilityDelta(findings=())
    new_state = apply_vulnerability_delta(state, delta)
    assert new_state is state or new_state.vuln_state == state.vuln_state

def test_apply_analysis_delta():
    state = get_base_state()
    # Add dummy evidence to satisfy Pydantic finding schema in delta_applier if it expects it
    delta = AnalysisDelta(grouped_findings=[{"endpoint": "/api", "subdomains": ["s1"], "evidence": "test"}])
    new_state = apply_analysis_delta(state, delta)
    assert new_state is not state
    assert len(new_state.findings) == 1

def test_apply_report_delta():
    from schemas.state import Report
    state = get_base_state()
    r1 = Report(id="r1", session_id="1", report_path="test.md", report_format="markdown", timestamp=datetime.now(timezone.utc))
    delta = ReportDelta(reports=(r1,))
    new_state = apply_report_delta(state, delta)
    assert new_state is not state
    assert len(new_state.reports) == 1
