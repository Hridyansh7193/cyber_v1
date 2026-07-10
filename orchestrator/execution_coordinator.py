from typing import Tuple, Callable
from schemas.state import ExecutionState
from schemas.tool_result import ToolResult
from schemas.runtime import Capability
from config.schemas import BugHunterConfig

class ExecutionCoordinator:
    """Coordinates execution of plugins through wrappers based on the TaskQueue."""
    
    @staticmethod
    def execute_capability(
        state: ExecutionState, 
        config: BugHunterConfig, 
        capability: Capability,
        wrapper_func: Callable[[Tuple[str, ...], BugHunterConfig, ExecutionState], Tuple[ToolResult, ...]]
    ) -> Tuple[ToolResult, ...]:
        
        # Determine prefix for this capability
        prefix = ""
        if capability == Capability.RECON:
            prefix = "plugin:recon:"
        elif capability == Capability.JS:
            prefix = "plugin:js:"
        elif capability == Capability.API:
            prefix = "plugin:api:"
        elif capability == Capability.VULN:
            prefix = "plugin:vuln:"
            
        plugin_names = []
        for task in state.task_queue:
            if task.name.startswith(prefix):
                plugin_names.append(task.name[len(prefix):])
                
        if not plugin_names:
            return ()
            
        # Future architecture hook: handle retries, cancellation, timeouts, telemetry here
        return wrapper_func(tuple(plugin_names), config, state)
