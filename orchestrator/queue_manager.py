from orchestrator.orchestration_state import OrchestrationState, TaskStatus

def update_task_status(state: OrchestrationState, task_name: str, status: TaskStatus) -> OrchestrationState:
    new_statuses = dict(state.task_status)
    new_statuses[task_name] = status
    
    return OrchestrationState(
        task_status=new_statuses,
        errors=state.errors
    )

def start_task(state: OrchestrationState, task_name: str) -> OrchestrationState:
    return update_task_status(state, task_name, "RUNNING")

def complete_task(state: OrchestrationState, task_name: str) -> OrchestrationState:
    return update_task_status(state, task_name, "COMPLETED")
