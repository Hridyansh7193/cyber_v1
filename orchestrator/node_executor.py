from typing import Callable, Any
from config.schemas import BugHunterConfig
from schemas.state import ExecutionState

def execute_node(
    current_exec: ExecutionState,
    config: BugHunterConfig,
    wrapper: Callable[[Any], Any],
    wrapper_applier: Callable[[Any, Any], Any],
    agent: Callable[[Any, Any], Any],
    delta_applier: Callable[[Any, Any], Any]
) -> ExecutionState:
    # 1. Wrapper
    if wrapper and wrapper_applier:
        wrapper_out = wrapper(current_exec)
        current_exec = wrapper_applier(current_exec, wrapper_out)
        
    # 2. Agent
    if agent and delta_applier:
        delta = agent(current_exec, config)
        current_exec = delta_applier(current_exec, delta)
        
    return current_exec
