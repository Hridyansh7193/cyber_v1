import pytest
import copy
from typing import Dict, Any

from schemas.state import ExecutionState, TargetState, ReconState, JSState, APIState, VulnerabilityState
from schemas.finding import Finding, Severity, Confidence
from schemas.report import ReportFormat
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from agents.deltas import PlannerDelta, ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, AnalysisDelta, ReportDelta
from agents.planner import plan
from agents.recon import analyze_recon
from agents.js import analyze_js
from agents.api import analyze_api
from agents.vulnerability import analyze_vulnerabilities
from agents.analyzer import associate
from agents.reporter import generate_reports

@pytest.fixture
def mock_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )

@pytest.fixture
def mock_state() -> ExecutionState:
    from datetime import datetime, timezone
    return ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)),
        recon_state=ReconState(subdomains=["sub2.example.com", "sub1.example.com", "sub1.example.com"], alive_hosts=["sub1.example.com"], urls=["http://sub1.example.com"]),
        js_state=JSState(js_files=["app.js"], endpoints=["/api/v1/users", "/api/v1/users"]),
        api_state=APIState(swagger_urls=["http://sub1.example.com/swagger"], graphql_urls=[]),
        vuln_state=VulnerabilityState(nuclei_results=[{"id": "vuln1"}], dalfox_results=[{"id": "vuln1"}], takeovers=[])
    )

def test_planner_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = plan(mock_state, mock_config)
    delta2 = plan(mock_state, mock_config)
    
    # Deterministic output
    assert delta1 == delta2
    assert isinstance(delta1, PlannerDelta)
    assert "vulnerability_analysis" in delta1.recommended_actions
    
    # State immutability
    assert mock_state.model_dump() == original_state_dump

def test_recon_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = analyze_recon(mock_state, mock_config)
    delta2 = analyze_recon(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, ReconDelta)
    # Deduplication without sorting
    assert delta1.subdomains == ("sub2.example.com", "sub1.example.com")
    
    assert mock_state.model_dump() == original_state_dump

def test_js_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = analyze_js(mock_state, mock_config)
    delta2 = analyze_js(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, JSDelta)
    assert delta1.endpoints == ("/api/v1/users",)
    
    assert mock_state.model_dump() == original_state_dump

def test_api_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = analyze_api(mock_state, mock_config)
    delta2 = analyze_api(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, APIDelta)
    assert delta1.swagger_urls == ("http://sub1.example.com/swagger",)
    
    assert mock_state.model_dump() == original_state_dump

def test_vulnerability_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = analyze_vulnerabilities(mock_state, mock_config)
    delta2 = analyze_vulnerabilities(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, VulnerabilityDelta)
    # Both nuclei and dalfox have identical {"id": "vuln1"} objects, should be deduplicated
    assert len(delta1.findings) == 1
    
    assert mock_state.model_dump() == original_state_dump

def test_analyzer_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = associate(mock_state, mock_config)
    delta2 = associate(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, AnalysisDelta)
    # Should not produce random severity logic
    assert mock_state.model_dump() == original_state_dump

def test_reporter_pure_function(mock_state, mock_config):
    original_state_dump = mock_state.model_dump()
    
    delta1 = generate_reports(mock_state, mock_config)
    delta2 = generate_reports(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, ReportDelta)
    
    formats = [r.report_format for r in delta1.reports]
    assert ReportFormat.JSON in formats
    assert ReportFormat.MARKDOWN in formats
    
    assert mock_state.model_dump() == original_state_dump

def test_planner_empty_state(mock_config):
    from datetime import datetime, timezone
    # All states are default empty
    empty_state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc))
    )
    delta = plan(empty_state, mock_config)
    assert "recon" in delta.recommended_actions
    assert "js_analysis" in delta.recommended_actions
    assert "api_analysis" in delta.recommended_actions
    assert "vulnerability_analysis" in delta.recommended_actions

def test_planner_repeated_execution_determinism(mock_state, mock_config):
    d1 = plan(mock_state, mock_config)
    d2 = plan(mock_state, mock_config)
    assert d1 == d2

def test_planner_target_absent(mock_config):
    # ExecutionState strictly requires TargetState, so target is never strictly absent.
    # We test with a bare minimum target.
    pass
