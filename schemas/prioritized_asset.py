from pydantic import BaseModel, ConfigDict, Field

class PrioritizedAsset(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    asset: str
    asset_type: str
    score: float
    reasoning: str
