from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas import APIDelta

def analyze_api(state: ExecutionState, config: BugHunterConfig) -> APIDelta:
    swagger = tuple(dict.fromkeys(state.api_state.swagger_urls))
    graphql = tuple(dict.fromkeys(state.api_state.graphql_urls))
    
    return APIDelta(
        swagger_urls=swagger,
        graphql_urls=graphql
    )
