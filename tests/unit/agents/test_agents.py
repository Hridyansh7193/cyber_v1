import pytest

from schemas.state import ExecutionState, TargetState, ReconState, JSState, APIState, VulnerabilityState
from schemas.report import ReportFormat
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from agents.deltas import TaskQueueDelta, ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, FindingDelta, ReportDelta
from agents.planner_agent import plan
from agents.recon import analyze_recon
from agents.js import analyze_js
from agents.api import analyze_api
from agents.vulnerability import analyze_vulnerabilities
from agents.analyzer_agent import analyze_intelligence
from agents.reporter_agent import generate_reports

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
    assert isinstance(delta1, TaskQueueDelta)
    assert any(t.name == "node:vulnerability_node" for t in delta1.task_queue)
    
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
    
    delta1 = analyze_intelligence(mock_state, mock_config)
    delta2 = analyze_intelligence(mock_state, mock_config)
    
    assert delta1 == delta2
    assert isinstance(delta1, FindingDelta)
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

def test_reporter_empty_formats(mock_state, mock_config):
    config = mock_config.model_copy(update={"reporting": ReportingConfig(report_formats=[], output_directories={})})
    delta = generate_reports(mock_state, config)
    assert len(delta.reports) == 0

def test_reporter_markdown_generation(mock_state, mock_config):
    config = mock_config.model_copy(update={"reporting": ReportingConfig(report_formats=["markdown"], output_directories={"markdown": "out/md"})})
    delta = generate_reports(mock_state, config)
    assert len(delta.reports) == 1
    assert delta.reports[0].report_format == ReportFormat.MARKDOWN
    assert delta.reports[0].report_path == "out/md/report.markdown"

def test_reporter_json_generation(mock_state, mock_config):
    config = mock_config.model_copy(update={"reporting": ReportingConfig(report_formats=["json"], output_directories={"json": "out/json"})})
    delta = generate_reports(mock_state, config)
    assert len(delta.reports) == 1
    assert delta.reports[0].report_format == ReportFormat.JSON
    assert delta.reports[0].report_path == "out/json/report.json"

def test_reporter_uuid5_determinism(mock_state, mock_config):
    delta1 = generate_reports(mock_state, mock_config)
    delta2 = generate_reports(mock_state, mock_config)
    assert delta1.reports[0].report_id == delta2.reports[0].report_id
    assert delta1.reports[0].report_id.version == 5

def test_reporter_timestamp_determinism(mock_state, mock_config):
    delta1 = generate_reports(mock_state, mock_config)
    assert delta1.reports[0].created_at == mock_state.target.start_time

def test_reporter_malformed_configuration(mock_state, mock_config):
    config = mock_config.model_copy(update={"reporting": ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json"})})
    delta = generate_reports(mock_state, config)
    markdown_reports = [r for r in delta.reports if r.report_format == ReportFormat.MARKDOWN]
    assert len(markdown_reports) == 1
    assert markdown_reports[0].report_path == "reports/report.markdown"

def test_reporter_empty_findings(mock_state, mock_config):
    from datetime import datetime, timezone
    empty_state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)),
        findings=()
    )
    delta = generate_reports(empty_state, mock_config)
    for report in delta.reports:
        assert len(report.findings) == 0
        assert report.total_findings == 0

def test_reporter_invalid_format(mock_state, mock_config):
    config = mock_config.model_copy(update={"reporting": ReportingConfig(report_formats=["json", "invalid_format"], output_directories={"json": "out/json"})})
    delta = generate_reports(mock_state, config)
    assert len(delta.reports) == 1
    assert delta.reports[0].report_format == ReportFormat.JSON

def test_planner_empty_state(mock_config):
    from datetime import datetime, timezone
    empty_state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc))
    )
    delta = plan(empty_state, mock_config)
    tasks = [t.name for t in delta.task_queue]
    assert "node:passive_recon_node" in tasks
    assert "node:js_node" in tasks
    assert "node:api_node" in tasks
    assert "node:vulnerability_node" in tasks

def test_planner_repeated_execution_determinism(mock_state, mock_config):
    d1 = plan(mock_state, mock_config)
    d2 = plan(mock_state, mock_config)
    assert d1 == d2
