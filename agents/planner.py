from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas import PlannerDelta

def plan(state: ExecutionState, config: BugHunterConfig) -> PlannerDelta:
    actions = []
    
    # Very basic static planning logic for Phase 7 (pure functional)
    if not state.recon_state.subdomains:
        actions.append("recon")
    
    if not state.js_state.js_files:
        actions.append("js_analysis")
        
    if not state.api_state.swagger_urls and not state.api_state.graphql_urls:
        actions.append("api_analysis")
        
    actions.append("vulnerability_analysis")
    
    return PlannerDelta(recommended_actions=tuple(actions))
