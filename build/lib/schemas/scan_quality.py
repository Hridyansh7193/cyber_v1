from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ScoreComponent(BaseModel):
    model_config = ConfigDict(frozen=True)
    value: float = Field(default=0.0)
    formula: str = Field(default="")
    reasoning: str = Field(default="")

class ScanQuality(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    coverage_score: Optional[ScoreComponent] = Field(default=None)
    recon_confidence: Optional[ScoreComponent] = Field(default=None)
    api_coverage: Optional[ScoreComponent] = Field(default=None)
    js_coverage: Optional[ScoreComponent] = Field(default=None)
    attack_surface_coverage: Optional[ScoreComponent] = Field(default=None)
    evidence_completeness: Optional[ScoreComponent] = Field(default=None)
    planner_confidence: Optional[ScoreComponent] = Field(default=None)
    correlation_quality: Optional[ScoreComponent] = Field(default=None)
    attack_graph_completeness: Optional[ScoreComponent] = Field(default=None)
    overall_scan_quality: Optional[ScoreComponent] = Field(default=None)
