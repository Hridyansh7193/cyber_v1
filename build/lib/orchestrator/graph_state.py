from typing import TypedDict
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState

class GraphState(TypedDict):
    execution_state: ExecutionState
    orchestration_state: OrchestrationState
