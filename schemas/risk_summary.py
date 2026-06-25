from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple

class RiskSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    score: float = Field(default=0.0)
    level: str = Field(default="INFO")
    reasoning: str = Field(default="")
