import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.node_result import NodeResult
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from orchestrator.nodes.recon_node import recon_node
from orchestrator.nodes.js_node import js_node
from orchestrator.nodes.api_node import api_node
from orchestrator.nodes.vulnerability_node import vulnerability_node
from orchestrator.nodes.analysis_node import analysis_node
from orchestrator.nodes.report_node import report_node

@pytest.fixture
def mock_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )

def get_base_state():
    exec_state = ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={}, errors={})
    return NodeResult(execution_state=exec_state, orchestration_state=orch_state)

def test_recon_node(mock_config):
    res = recon_node(get_base_state(), mock_config)
    assert res.orchestration_state.task_status["recon"] == "COMPLETED"

def test_js_node(mock_config):
    res = js_node(get_base_state(), mock_config)
    assert res.orchestration_state.task_status["js"] == "COMPLETED"

def test_api_node(mock_config):
    res = api_node(get_base_state(), mock_config)
    assert res.orchestration_state.task_status["api"] == "COMPLETED"

def test_vuln_node(mock_config):
    res = vulnerability_node(get_base_state(), mock_config)
    assert res.orchestration_state.task_status["vulnerability"] == "COMPLETED"

def test_analysis_node(mock_config):
    res = analysis_node(get_base_state(), mock_config)
    assert res.orchestration_state.task_status["analysis"] == "COMPLETED"

def test_report_node(mock_config):
    res = report_node(get_base_state(), mock_config)
    assert res.orchestration_state.task_status["report"] == "COMPLETED"
