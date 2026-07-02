from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_parameter_wrapper_result
from orchestrator.queue_manager import start_task, complete_task
from execution.wrappers import ParameterWrapper
from schemas.runtime import Capability

def parameter_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    if state.execution_state.intelligence and state.execution_state.intelligence.planner:
        if "parameter_node" in state.execution_state.intelligence.planner.skipped_nodes:
            new_orch = start_task(state.orchestration_state, "parameter")
            new_orch = complete_task(new_orch, "parameter")
            return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)

    orch = start_task(state.orchestration_state, "parameter")
    
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        capability=Capability.PARAMETER_DISCOVERY,
        wrapper_func=ParameterWrapper.execute,
        wrapper_applier=apply_parameter_wrapper_result,
        agent=None,
        delta_applier=None
    )
    orch = complete_task(orch, "parameter")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
