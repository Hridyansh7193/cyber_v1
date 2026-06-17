import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.node_executor import execute_node

def get_base_state():
    return ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))

def test_wrapper_exception_propagation():
    def failing_wrapper(state):
        raise ValueError("Wrapper failed")
    
    with pytest.raises(ValueError, match="Wrapper failed"):
        execute_node(get_base_state(), None, failing_wrapper, lambda s, r: s, None, None)

def test_agent_exception_propagation():
    def failing_agent(state, config):
        raise TypeError("Agent failed")
        
    with pytest.raises(TypeError, match="Agent failed"):
        execute_node(get_base_state(), None, None, None, failing_agent, lambda s, r: s)

def test_wrapper_result_applier_exception():
    def failing_applier(state, result):
        raise RuntimeError("Applier failed")
        
    with pytest.raises(RuntimeError, match="Applier failed"):
        execute_node(get_base_state(), None, lambda s: "res", failing_applier, None, None)

def test_delta_applier_exception():
    def failing_applier(state, delta):
        raise OSError("Delta failed")
        
    with pytest.raises(OSError, match="Delta failed"):
        execute_node(get_base_state(), None, None, None, lambda s, c: "delta", failing_applier)

def test_successful_execution():
    state = get_base_state()
    res = execute_node(state, None, lambda s: "res", lambda s, r: s, lambda s, c: "delta", lambda s, d: s)
    assert res is state
