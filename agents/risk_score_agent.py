from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.risk_summary import RiskSummary

def score_risk(state: ExecutionState, config: BugHunterConfig) -> RiskSummary:
    # Placeholder logic for Risk Scoring Phase 14
    # Compute simple max severity
    severity_map = {"critical": 10.0, "high": 8.0, "medium": 5.0, "low": 2.0, "info": 0.0}
    
    max_score = 0.0
    max_level = "INFO"
    
    for finding in state.findings:
        score = severity_map.get(finding.severity.lower(), 0.0)
        if score > max_score:
            max_score = score
            max_level = finding.severity.upper()
            
    reasoning = f"Highest finding severity is {max_level}" if max_score > 0 else "No significant findings"
    
    return RiskSummary(
        score=max_score,
        level=max_level,
        reasoning=reasoning
    )
