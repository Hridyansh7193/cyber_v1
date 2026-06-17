from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_js_wrapper_result
from agents.js import analyze_js
from orchestrator.delta_applier import apply_js_delta

def dummy_js_wrapper(state):
    return {"new_js_files": [], "new_endpoints": []}

def js_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    return execute_node(
        state=state,
        config=config,
        task_name="js",
        wrapper=dummy_js_wrapper,
        wrapper_applier=apply_js_wrapper_result,
        agent=analyze_js,
        delta_applier=apply_js_delta
    )
