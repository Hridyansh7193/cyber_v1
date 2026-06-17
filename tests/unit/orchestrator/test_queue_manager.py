import pytest
from orchestrator.queue_manager import update_task_status, start_task, complete_task
from orchestrator.orchestration_state import OrchestrationState

def test_start_task():
    state = OrchestrationState(task_status={}, errors={})
    new_state = start_task(state, "recon")
    assert new_state.task_status["recon"] == "RUNNING"

def test_complete_task():
    state = OrchestrationState(task_status={"recon": "RUNNING"}, errors={})
    new_state = complete_task(state, "recon")
    assert new_state.task_status["recon"] == "COMPLETED"

def test_fail_task():
    state = OrchestrationState(task_status={"recon": "RUNNING"}, errors={})
    new_state = update_task_status(state, "recon", "FAILED")
    assert new_state.task_status["recon"] == "FAILED"

def test_cancel_task():
    state = OrchestrationState(task_status={"recon": "RUNNING"}, errors={})
    new_state = update_task_status(state, "recon", "CANCELLED")
    assert new_state.task_status["recon"] == "CANCELLED"
