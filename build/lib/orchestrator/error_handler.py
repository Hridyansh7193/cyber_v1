from orchestrator.orchestration_state import OrchestrationState
from orchestrator.queue_manager import update_task_status

def handle_task_error(state: OrchestrationState, task_name: str, error_msg: str) -> OrchestrationState:
    # If cancelled, mark as CANCELLED, else FAILED
    status = "CANCELLED" if "cancel" in error_msg.lower() else "FAILED"
    state_failed = update_task_status(state, task_name, status)
    
    # Attach error metadata
    new_errors = dict(state_failed.errors)
    if task_name not in new_errors:
        new_errors[task_name] = []
    new_errors[task_name] = new_errors[task_name] + [error_msg]
    
    # Return updated state
    return OrchestrationState(
        task_status=state_failed.task_status,
        errors=new_errors
    )
