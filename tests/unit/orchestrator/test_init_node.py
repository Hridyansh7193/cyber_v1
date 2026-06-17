import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.node_result import NodeResult
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig
from orchestrator.nodes.init_node import init_node

@pytest.fixture
def mock_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings=SettingsConfig(scan_depth=1, max_concurrency=5, log_level="INFO"),
        llm=LLMConfig(provider="openai", default_model="gpt-4", timeout=30),
        tools=ToolsConfig(tool_paths={}, docker_container_names={}, wordlists={}, enable_flags={}),
        timeouts=TimeoutsConfig(subfinder_timeout=10, nuclei_timeout=10, dalfox_timeout=10, ffuf_timeout=10, global_timeout=10),
        reporting=ReportingConfig(report_formats=["json", "markdown"], output_directories={"json": "out/json", "markdown": "out/markdown"})
    )

def test_init_node_populated_target(mock_config):
    exec_state = ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="12345", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={"init": "PENDING"}, errors={})
    nr = NodeResult(execution_state=exec_state, orchestration_state=orch_state)
    
    res = init_node(nr, mock_config)
    
    assert res.orchestration_state.task_status["init"] == "COMPLETED"
    assert res.execution_state.target.session_id == "12345"

def test_init_node_empty_target(mock_config):
    exec_state = ExecutionState(target=TargetState(domain="", scope=[], session_id="", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={}, errors={})
    nr = NodeResult(execution_state=exec_state, orchestration_state=orch_state)
    
    res = init_node(nr, mock_config)
    
    assert res.orchestration_state.task_status["init"] == "COMPLETED"
    assert res.execution_state.target.domain == ""
    
def test_init_node_default_orchestration(mock_config):
    exec_state = ExecutionState(target=TargetState(domain="", scope=[], session_id="", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={}, errors={})
    nr = NodeResult(execution_state=exec_state, orchestration_state=orch_state)
    
    res = init_node(nr, mock_config)
    assert "init" in res.orchestration_state.task_status
    assert res.orchestration_state.task_status["init"] == "COMPLETED"
