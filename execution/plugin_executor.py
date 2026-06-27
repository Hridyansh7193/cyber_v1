from typing import Tuple, List, Any
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugins.registry import REGISTRY
from execution.plugins.base import ExecutionPlugin
from execution.utils.process_runner import ProcessRunner

class PluginExecutor:
    """Handles the execution of plugins, enforcing validation."""
    
    @staticmethod
    def execute_plugins(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: Any, result_key: str = "new_findings") -> Tuple[ToolResult, ...]:
        results: List[ToolResult] = []
        
        for name in plugin_names:
            plugin: ExecutionPlugin = REGISTRY.get_plugin(name)
            if not plugin:
                continue
                
            if not plugin.validate(target, {}):
                continue
                
            # Execute
            command = plugin.build_command(target, {})
            exit_code, stdout, stderr, execution_time = ProcessRunner.run(list(command), plugin.metadata().name)
            
            parsed = []
            errors = []
            if exit_code == 0:
                try:
                    parsed = plugin.parse(stdout, stderr)
                except Exception as e:
                    errors.append(f"Parse error: {str(e)}")
            else:
                errors.append(f"Execution failed with exit code {exit_code}")
                
            tool_res = ToolResult(
                tool_name=plugin.metadata().name,
                plugin_version=plugin.metadata().version,
                success=exit_code == 0 and len(errors) == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                stdout_size=len(stdout),
                parsed_findings=len(parsed) if isinstance(parsed, list) else 0,
                errors=tuple(errors),
                execution_time=execution_time,
                metadata={result_key: parsed}
            )
            results.append(tool_res)
            
        return tuple(results)
