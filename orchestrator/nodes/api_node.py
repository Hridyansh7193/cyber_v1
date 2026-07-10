from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_api_wrapper_result
from agents.api import analyze_api
from orchestrator.delta_applier import apply_api_delta
from orchestrator.queue_manager import start_task, complete_task
from execution.wrappers import APIWrapper
from schemas.runtime import Capability

def api_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    if not any(t.name == "node:api_node" for t in state.execution_state.task_queue):
        new_orch = start_task(state.orchestration_state, "api")
        new_orch = complete_task(new_orch, "api")
        return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)

    orch = start_task(state.orchestration_state, "api")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        capability=Capability.API,
        wrapper_func=APIWrapper.execute,
        wrapper_applier=apply_api_wrapper_result,
        agent=analyze_api,
        delta_applier=apply_api_delta
    )
    orch = complete_task(orch, "api")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
