from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple, Optional
from .planner_decision import PlannerDecision
from .prioritized_asset import PrioritizedAsset
from .correlated_finding import CorrelatedFinding
from .attack_graph import AttackGraph
from .risk_summary import RiskSummary

class IntelligenceState(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    version: int = Field(default=1)
    planner: Optional[PlannerDecision] = Field(default=None)
    prioritized_assets: Tuple[PrioritizedAsset, ...] = Field(default=())
    correlated_findings: Tuple[CorrelatedFinding, ...] = Field(default=())
    attack_graph: Optional[AttackGraph] = Field(default=None)
    risk_summary: Optional[RiskSummary] = Field(default=None)
