from typing import Tuple, Callable
from schemas.state import ExecutionState
from schemas.tool_result import ToolResult
from schemas.runtime import Capability
from config.schemas import BugHunterConfig

class ExecutionCoordinator:
    """Coordinates execution of plugins through wrappers based on the Planner's ExecutionPlan."""
    
    @staticmethod
    def execute_capability(
        state: ExecutionState, 
        config: BugHunterConfig, 
        capability: Capability,
        wrapper_func: Callable[[Tuple[str, ...], BugHunterConfig, ExecutionState], Tuple[ToolResult, ...]]
    ) -> Tuple[ToolResult, ...]:
        
        plan = None
        if state.intelligence and state.intelligence.planner:
            plan = state.intelligence.planner.execution_plan
            
        if not plan:
            return ()
            
        plugin_names = ()
        if capability == Capability.RECON:
            plugin_names = plan.recon_plugins
        elif capability == Capability.JS:
            plugin_names = plan.js_plugins
        elif capability == Capability.API:
            plugin_names = plan.api_plugins
        elif capability == Capability.VULN:
            plugin_names = plan.vuln_plugins
            
        if not plugin_names:
            return ()
            
        # Future architecture hook: handle retries, cancellation, timeouts, telemetry here
        return wrapper_func(plugin_names, config, state)
