from pydantic import BaseModel, ConfigDict
from schemas.intelligence import IntelligenceState

class IntelligenceDelta(BaseModel):
    model_config = ConfigDict(frozen=True)
    intelligence: IntelligenceState
