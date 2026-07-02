import pytest
from orchestrator.error_handler import handle_task_error
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.transitions import passive_recon_transition
from orchestrator.graph_state import GraphState

def test_handle_error_retry_exhausted():
    # Verify task becomes FAILED
    state = OrchestrationState(task_status={"passive_recon": "RUNNING"}, errors={})
    new_state = handle_task_error(state, "passive_recon", "TimeoutError")
    assert new_state.task_status["passive_recon"] == "FAILED"
    assert "TimeoutError" in new_state.errors["passive_recon"]

def test_handle_error_cancellation():
    # Verify CANCELLED state
    state = OrchestrationState(task_status={"passive_recon": "RUNNING"}, errors={})
    new_state = handle_task_error(state, "passive_recon", "User cancelled")
    assert new_state.task_status["passive_recon"] == "CANCELLED"

def test_handle_error_graceful_continuation():
    # Verify pipeline continues toward REPORT when FAILED or CANCELLED
    state = OrchestrationState(task_status={"passive_recon": "FAILED"}, errors={})
    graph_state: GraphState = {"execution_state": None, "orchestration_state": state}
    # passive_recon_transition routes to js_node if COMPLETED or FAILED or CANCELLED
    # Let's ensure our transitions.py supports CANCELLED too, or FAILED is enough to continue
    assert passive_recon_transition(graph_state) == "scope_enforcement_node"
    
def test_handle_error_exception_mapping():
    # Verify errors are preserved
    state = OrchestrationState(task_status={"passive_recon": "RUNNING"}, errors={})
    new_state = handle_task_error(state, "recon", "ConnectionError")
    assert "ConnectionError" in new_state.errors["recon"]
