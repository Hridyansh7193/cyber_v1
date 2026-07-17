from pydantic import BaseModel, ConfigDict
from schemas.state import ExecutionState
from orchestrator.orchestration_state import OrchestrationState

class NodeResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    execution_state: ExecutionState
    orchestration_state: OrchestrationState
