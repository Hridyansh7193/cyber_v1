from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple

class PlannerDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    execute_nodes: Tuple[str, ...] = Field(default=())
    skipped_nodes: Tuple[str, ...] = Field(default=())
    priority_overrides: Tuple[str, ...] = Field(default=())
    reasoning: str = Field(default="")
    confidence: float = Field(default=0.0)
