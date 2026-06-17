from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas import JSDelta

def analyze_js(state: ExecutionState, config: BugHunterConfig) -> JSDelta:
    # Aggregate and deduplicate
    files = tuple(dict.fromkeys(state.js_state.js_files))
    endpoints = tuple(dict.fromkeys(state.js_state.endpoints))
    
    return JSDelta(
        js_files=files,
        endpoints=endpoints
    )
