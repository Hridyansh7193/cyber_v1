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
        if capability in (Capability.RECON, Capability.PASSIVE_RECON, Capability.DNS, Capability.HTTP):
            prefix = "plugin:recon:"
        elif capability == Capability.JS:
            prefix = "plugin:js:"
        elif capability == Capability.API:
            prefix = "plugin:api:"
        elif capability == Capability.VULN:
            prefix = "plugin:vuln:"
        elif capability == Capability.PARAMETER_DISCOVERY:
            # Although parameter tools are in recon, wait parameter wrapper is just a generic executor.
            prefix = "plugin:vuln:" # we'll catch it or we'll rely on the capability matching. Actually parameter_node doesn't even use this wrapper. Wait, parameter_node uses ParameterWrapper.execute
            
        plugin_names = []
        from execution.plugins.registry import REGISTRY
        for task in state.task_queue:
            if task.name.startswith(prefix):
                name = task.name[len(prefix):]
                plugin = REGISTRY.get_plugin(name)
                # Verify the plugin actually has the requested capability
                if plugin and capability in plugin.metadata().capabilities:
                    plugin_names.append(name)
                
        if not plugin_names:
            return ()
            
        # Future architecture hook: handle retries, cancellation, timeouts, telemetry here
        return wrapper_func(tuple(plugin_names), config, state)
