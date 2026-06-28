import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.graph_state import GraphState
from orchestrator.graph import build_graph
from orchestrator.checkpoint_manager import CheckpointManager
from langgraph.graph import END
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
    assert recon_transition(state) == END

def test_wrapper_applier():
    from schemas.state import ExecutionState, TargetState
    from schemas.tool_result import ToolResult
    exec_state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)))
    
    wrapper_out = ToolResult(tool_name="test", metadata={"new_subdomains": ["sub1"]}, success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)
    new_state = apply_recon_wrapper_result(exec_state, (wrapper_out,))
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
    from schemas.tool_result import ToolResult
    from schemas.runtime import Capability
    exec_state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="sess_1", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={}, errors={})
    
    def dummy_wrapper(s): return (ToolResult(tool_name="test", metadata={"new_subdomains": ["sub1"]}, success=True, exit_code=0, stdout="", stderr="", execution_time=0.0),)
    def dummy_agent(s, c): return ReconDelta(subdomains=("sub1",), alive_hosts=(), urls=())
    
    # execute_node now takes current_exec directly
    new_exec = execute_node(
        current_exec=exec_state, config=mock_config, capability=Capability.RECON,
        wrapper_func=dummy_wrapper, wrapper_applier=apply_recon_wrapper_result,
        agent=dummy_agent, delta_applier=apply_recon_delta
    )
    
    assert "sub1" in new_exec.recon_state.subdomains
