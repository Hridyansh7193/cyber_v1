from typing import Callable, Any
from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.queue_manager import update_task_status

def execute_node(
    state: NodeResult,
    config: BugHunterConfig,
    task_name: str,
    wrapper: Callable[[Any], Any],
    wrapper_applier: Callable[[Any, Any], Any],
    agent: Callable[[Any, Any], Any],
    delta_applier: Callable[[Any, Any], Any]
) -> NodeResult:
    # 1. Mark Running
    new_orch = update_task_status(state.orchestration_state, task_name, "RUNNING")
    current_exec = state.execution_state
    
    try:
        # 2. Wrapper
        if wrapper and wrapper_applier:
            wrapper_out = wrapper(current_exec)
            current_exec = wrapper_applier(current_exec, **wrapper_out)
            
        # 3. Agent
        if agent and delta_applier:
            delta = agent(current_exec, config)
            current_exec = delta_applier(current_exec, delta)
            
        # 4. Mark Completed
        final_orch = update_task_status(new_orch, task_name, "COMPLETED")
        return NodeResult(execution_state=current_exec, orchestration_state=final_orch)
        
    except Exception as e:
        # We re-raise to let langgraph handle retry/error_handler
        raise e
