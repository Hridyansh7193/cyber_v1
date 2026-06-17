import pytest
from datetime import datetime, timezone
from schemas.state import ExecutionState, TargetState
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.state_adapter import to_graph_state, from_graph_state
from orchestrator.graph_state import GraphState
from orchestrator.node_result import NodeResult

def test_state_adapter():
    exec_state = ExecutionState(target=TargetState(domain="test.com", scope=[], session_id="1", start_time=datetime.now(timezone.utc)))
    orch_state = OrchestrationState(task_status={"test": "COMPLETED"}, errors={})
    graph_state: GraphState = {"execution_state": exec_state, "orchestration_state": orch_state}
    
    nr = from_graph_state(graph_state)
    assert isinstance(nr, NodeResult)
    assert nr.orchestration_state.task_status["test"] == "COMPLETED"
    
    new_graph_state = to_graph_state(nr)
    assert "execution_state" in new_graph_state
    assert "orchestration_state" in new_graph_state
    assert new_graph_state["orchestration_state"].task_status["test"] == "COMPLETED"
    
    # Prove no sharing between nr and new_graph_state (NodeResult is pure)
    assert new_graph_state["orchestration_state"] is nr.orchestration_state
