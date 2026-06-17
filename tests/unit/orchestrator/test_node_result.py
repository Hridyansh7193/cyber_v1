import pytest
from datetime import datetime, timezone
from orchestrator.node_result import NodeResult
from schemas.state import ExecutionState, TargetState
from orchestrator.orchestration_state import OrchestrationState

def test_node_result():
    exec_state = ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={}, errors={})
    
    nr = NodeResult(execution_state=exec_state, orchestration_state=orch_state)
    
    # Prove NodeResult contains ONLY execution_state and orchestration_state
    assert hasattr(nr, "execution_state")
    assert hasattr(nr, "orchestration_state")
    assert not hasattr(nr, "errors")
    
    # Prove errors are in orchestration_state
    assert hasattr(nr.orchestration_state, "errors")
