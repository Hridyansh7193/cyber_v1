from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas import AnalysisDelta

def associate(state: ExecutionState, config: BugHunterConfig) -> AnalysisDelta:
    # Cross references subdomains with endpoints
    grouped = []
    
    # Static association (no logic generation, no deductions)
    for endpoint in tuple(dict.fromkeys(state.js_state.endpoints)):
        associated_subs = tuple(dict.fromkeys([s for s in state.recon_state.subdomains if s in endpoint]))
        if associated_subs:
            grouped.append({
                "endpoint": endpoint,
                "subdomains": associated_subs
            })
            
    return AnalysisDelta(grouped_findings=tuple(grouped))
