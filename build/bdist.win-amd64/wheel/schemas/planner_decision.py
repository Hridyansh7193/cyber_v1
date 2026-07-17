from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple

class ExecutionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    # Map capability name to a tuple of plugin names to execute
    recon_plugins: Tuple[str, ...] = Field(default=())
    js_plugins: Tuple[str, ...] = Field(default=())
    api_plugins: Tuple[str, ...] = Field(default=())
    vuln_plugins: Tuple[str, ...] = Field(default=())

class PlannerDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    execute_nodes: Tuple[str, ...] = Field(default=())
    skipped_nodes: Tuple[str, ...] = Field(default=())
    execution_plan: ExecutionPlan = Field(default_factory=ExecutionPlan)
    priority_overrides: Tuple[str, ...] = Field(default=())
    reasoning: str = Field(default="")
    confidence: float = Field(default=0.0)

