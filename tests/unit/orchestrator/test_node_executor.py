import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.node_executor import execute_node

from schemas.task import Task, TaskPriority, TaskStatus
from schemas.runtime import Capability

def get_base_state():
    return ExecutionState(
        target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)),
        task_queue=(
            # Use the new canonical prefix: plugin:active_recon:<name>
            Task(name="plugin:active_recon:httpx", priority=TaskPriority.HIGH, status=TaskStatus.PENDING),
        )
    )

def test_wrapper_exception_propagation():
    def failing_wrapper(plugins, config, target):
        raise ValueError("Wrapper failed")
    
    with pytest.raises(ValueError, match="Wrapper failed"):
        execute_node(current_exec=get_base_state(), config=None, capability=Capability.RECON, wrapper_func=failing_wrapper, wrapper_applier=lambda s, r: s, agent=None, delta_applier=None)

def test_agent_exception_propagation():
    def failing_agent(state, config):
        raise TypeError("Agent failed")
        
    with pytest.raises(TypeError, match="Agent failed"):
        execute_node(current_exec=get_base_state(), config=None, capability=Capability.RECON, wrapper_func=None, wrapper_applier=None, agent=failing_agent, delta_applier=lambda s, r: s)

def test_wrapper_result_applier_exception():
    def failing_applier(state, result):
        raise RuntimeError("Applier failed")
        
    with pytest.raises(RuntimeError, match="Applier failed"):
        execute_node(current_exec=get_base_state(), config=None, capability=Capability.RECON, wrapper_func=lambda p, c, t: "res", wrapper_applier=failing_applier, agent=None, delta_applier=None)

def test_delta_applier_exception():
    def failing_applier(state, delta):
        raise OSError("Delta failed")
        
    with pytest.raises(OSError, match="Delta failed"):
        execute_node(current_exec=get_base_state(), config=None, capability=Capability.RECON, wrapper_func=None, wrapper_applier=None, agent=lambda s, c: "delta", delta_applier=failing_applier)

def test_successful_execution():
    state = get_base_state()
    res = execute_node(current_exec=state, config=None, capability=Capability.RECON, wrapper_func=lambda p, c, t: "res", wrapper_applier=lambda s, r: s, agent=lambda s, c: "delta", delta_applier=lambda s, d: s)
    assert res is state
