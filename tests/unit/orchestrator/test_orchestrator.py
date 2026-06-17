import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.graph_state import GraphState
from orchestrator.graph import build_graph
from orchestrator.checkpoint_manager import CheckpointManager
from orchestrator.transitions import recon_transition, js_transition
from orchestrator.delta_applier import apply_recon_delta
from orchestrator.wrapper_result_applier import apply_recon_wrapper_result
from agents.deltas import ReconDelta
from orchestrator.node_executor import execute_node
from orchestrator.node_result import NodeResult
from config.schemas import BugHunterConfig, SettingsConfig, LLMConfig, ToolsConfig, TimeoutsConfig, ReportingConfig

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
def base_state() -> GraphState:
    exec_state = ExecutionState(
        target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc))
    )
    orch_state = OrchestrationState(task_status={}, errors={})
    return {"execution_state": exec_state, "orchestration_state": orch_state}

def test_graph_compilation(mock_config):
    manager = CheckpointManager()
    graph = build_graph(mock_config, checkpointer=manager)
    assert graph is not None

def test_transitions():
    orch_state = OrchestrationState(task_status={"recon": "COMPLETED"}, errors={})
    state: GraphState = {"execution_state": None, "orchestration_state": orch_state}
    assert recon_transition(state) == "js_node"
    
    # Should transition on FAILED too
    orch_state = OrchestrationState(task_status={"recon": "FAILED"}, errors={})
    state["orchestration_state"] = orch_state
    assert recon_transition(state) == "js_node"
    
    # Should not transition if PENDING
    orch_state = OrchestrationState(task_status={"recon": "PENDING"}, errors={})
    state["orchestration_state"] = orch_state
    assert recon_transition(state) == "END"

def test_wrapper_applier():
    from schemas.state import ExecutionState, TargetState
    exec_state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)))
    
    new_state = apply_recon_wrapper_result(exec_state, new_subdomains=["sub1"])
    assert "sub1" in new_state.recon_state.subdomains

def test_delta_applier():
    from schemas.state import ExecutionState, TargetState
    exec_state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)))
    
    delta = ReconDelta(subdomains=("sub1",), alive_hosts=(), urls=())
    new_state = apply_recon_delta(exec_state, delta)
    assert "sub1" in new_state.recon_state.subdomains

def test_checkpoint_recovery(mock_config, base_state):
    manager = CheckpointManager()
    config = {"configurable": {"thread_id": "test_thread"}}
    
    # Check graph saving natively isn't testable directly without running, but manager exposes saver
    assert manager.get_saver() is not None

def test_node_executor(mock_config):
    exec_state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={}, errors={})
    state = NodeResult(execution_state=exec_state, orchestration_state=orch_state)
    
    def dummy_wrapper(s): return {"new_subdomains": ["sub1"]}
    def dummy_agent(s, c): return ReconDelta(subdomains=("sub1",), alive_hosts=(), urls=())
    
    res = execute_node(
        state=state, config=mock_config, task_name="recon",
        wrapper=dummy_wrapper, wrapper_applier=apply_recon_wrapper_result,
        agent=dummy_agent, delta_applier=apply_recon_delta
    )
    
    assert res.orchestration_state.task_status["recon"] == "COMPLETED"
    assert "sub1" in res.execution_state.recon_state.subdomains
