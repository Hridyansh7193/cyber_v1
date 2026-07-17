from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple

class CorrelatedFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    root_cause: str
    vulnerability_class: str
    affected_assets: Tuple[str, ...] = Field(default=())
    evidence: Tuple[str, ...] = Field(default=())
    severity: str
    confidence: float
