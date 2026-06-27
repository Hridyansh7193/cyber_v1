from typing import Callable, Any, Tuple
from config.schemas import BugHunterConfig
from schemas.state import ExecutionState
from schemas.tool_result import ToolResult
from schemas.runtime import Capability
from orchestrator.execution_coordinator import ExecutionCoordinator

def execute_node(
    current_exec: ExecutionState,
    config: BugHunterConfig,
    capability: Capability = None,
    wrapper_func: Callable[[Tuple[str, ...], BugHunterConfig, str], Tuple[ToolResult, ...]] = None,
    wrapper_applier: Callable[[Any, Any], Any] = None,
    agent: Callable[[Any, Any], Any] = None,
    delta_applier: Callable[[Any, Any], Any] = None
) -> ExecutionState:
    # 1. Wrapper
    if capability and wrapper_func and wrapper_applier:
        wrapper_out = ExecutionCoordinator.execute_capability(current_exec, config, capability, wrapper_func)
        current_exec = wrapper_applier(current_exec, wrapper_out)
        
    # 2. Agent
    if agent and delta_applier:
        delta = agent(current_exec, config)
        current_exec = delta_applier(current_exec, delta)
        
    return current_exec
