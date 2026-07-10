from typing import Tuple, Callable
from schemas.state import ExecutionState
from schemas.tool_result import ToolResult
from schemas.runtime import Capability
from config.schemas import BugHunterConfig
from utils.logger import get_logger

logger = get_logger("execution_coordinator")

# Maps a Capability to the task-queue name prefix used by the planner.
# Each capability MUST have a unique prefix so nodes don't run each other's plugins.
_CAPABILITY_PREFIX: dict[Capability, str] = {
    Capability.PASSIVE_RECON: "plugin:passive_recon:",
    Capability.RECON: "plugin:active_recon:",
    Capability.DNS: "plugin:dns:",
    Capability.HTTP: "plugin:http:",
    Capability.JS: "plugin:js:",
    Capability.API: "plugin:api:",
    Capability.VULN: "plugin:vuln:",
    Capability.PARAMETER_DISCOVERY: "plugin:parameter:",
}


class ExecutionCoordinator:
    """Coordinates execution of plugins through wrappers based on the TaskQueue."""
    
    @staticmethod
    def execute_capability(
        state: ExecutionState, 
        config: BugHunterConfig, 
        capability: Capability,
        wrapper_func: Callable[[Tuple[str, ...], BugHunterConfig, ExecutionState], Tuple[ToolResult, ...]]
    ) -> Tuple[ToolResult, ...]:
        
        prefix = _CAPABILITY_PREFIX.get(capability)
        if not prefix:
            logger.warning(f"No prefix mapping for capability {capability}. No plugins will run.")
            return ()
            
        plugin_names = []
        from execution.plugins.registry import REGISTRY
        for task in state.task_queue:
            if task.name.startswith(prefix):
                name = task.name[len(prefix):]
                plugin = REGISTRY.get_plugin(name)
                # Verify the plugin actually has the requested capability
                if plugin and capability in plugin.metadata().capabilities:
                    plugin_names.append(name)
                elif plugin:
                    logger.debug(
                        f"Plugin '{name}' matched prefix '{prefix}' but lacks capability "
                        f"{capability}. Skipping."
                    )
                
        if not plugin_names:
            logger.debug(f"No plugins found for capability {capability} (prefix='{prefix}').")
            return ()
            
        logger.debug(f"ExecutionCoordinator: running {plugin_names} for capability {capability}.")
        # Future architecture hook: handle retries, cancellation, timeouts, telemetry here
        return wrapper_func(tuple(plugin_names), config, state)
