from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_js_wrapper_result
from agents.js import analyze_js
from orchestrator.delta_applier import apply_js_delta
from orchestrator.queue_manager import start_task, complete_task
from execution.wrappers import JSWrapper
from schemas.runtime import Capability

def js_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    if not any(t.name == "node:js_node" for t in state.execution_state.task_queue):
        new_orch = start_task(state.orchestration_state, "js")
        new_orch = complete_task(new_orch, "js")
        return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)

    orch = start_task(state.orchestration_state, "js")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        capability=Capability.JS,
        wrapper_func=JSWrapper.execute,
        wrapper_applier=apply_js_wrapper_result,
        agent=analyze_js,
        delta_applier=apply_js_delta
    )
    orch = complete_task(orch, "js")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
