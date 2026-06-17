from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_api_wrapper_result
from agents.api import analyze_api
from orchestrator.delta_applier import apply_api_delta

def dummy_api_wrapper(state):
    return {"new_swagger": [], "new_graphql": []}

def api_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    return execute_node(
        state=state,
        config=config,
        task_name="api",
        wrapper=dummy_api_wrapper,
        wrapper_applier=apply_api_wrapper_result,
        agent=analyze_api,
        delta_applier=apply_api_delta
    )
