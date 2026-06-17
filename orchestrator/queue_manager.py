from typing import Dict, List, Any
from orchestrator.orchestration_state import OrchestrationState, TaskStatus

def update_task_status(state: OrchestrationState, task_name: str, status: TaskStatus) -> OrchestrationState:
    new_statuses = dict(state.task_status)
    new_statuses[task_name] = status
    
    return OrchestrationState(
        task_status=new_statuses,
        errors=state.errors
    )
