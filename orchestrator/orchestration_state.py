from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Literal

TaskStatus = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]

class OrchestrationState(BaseModel):
    model_config = ConfigDict(frozen=True)
    task_status: Dict[str, TaskStatus]
    errors: Dict[str, List[str]]
    plugin_offsets: Dict[str, int] = Field(default_factory=dict)

