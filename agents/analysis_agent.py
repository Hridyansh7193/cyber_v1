from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas.intelligence_delta import IntelligenceDelta
from schemas.intelligence import IntelligenceState

from .correlation_agent import correlate
from .prioritizer_agent import prioritize
from .attack_graph_agent import generate_graph
from .risk_score_agent import score_risk

def analyze_intelligence(state: ExecutionState, config: BugHunterConfig) -> IntelligenceDelta:
    correlated_findings = correlate(state, config)
    prioritized_assets = prioritize(state, config)
    attack_graph = generate_graph(state, config)
    risk_summary = score_risk(state, config)
    
    # We create a new IntelligenceState containing just the new fields.
    # The DeltaApplier will merge these with the existing planner decision.
    intelligence = IntelligenceState(
        correlated_findings=correlated_findings,
        prioritized_assets=prioritized_assets,
        attack_graph=attack_graph,
        risk_summary=risk_summary
    )
    
    return IntelligenceDelta(intelligence=intelligence)
