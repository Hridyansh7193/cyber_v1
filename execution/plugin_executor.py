from typing import Tuple, List, Any
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugins.registry import REGISTRY
from execution.plugins.base import ExecutionPlugin
from execution.utils.process_runner import ProcessRunner
from execution.constants import METADATA_SCHEMA_VERSION, ToolMetadata
from utils.logger import get_logger

logger = get_logger("plugin_executor")

class PluginExecutor:
    """Handles the execution of plugins, enforcing validation."""
    
    @staticmethod
    def execute_plugins(plugin_names: Tuple[str, ...], config: BugHunterConfig, target: Any) -> Tuple[ToolResult, ...]:
        results: List[ToolResult] = []
        
        for name in plugin_names:
            plugin: ExecutionPlugin = REGISTRY.get_plugin(name)
            if not plugin:
                continue
                
            if not plugin.validate(target, {}):
                continue
                
            # Execute
            command = plugin.build_command(target, {})
            logger.info(f"{plugin.metadata().name} started")
            result = ProcessRunner.run(list(command), plugin.metadata().name)
            logger.info(f"{plugin.metadata().name} finished in {result.execution_time:.2f}s (Exit code: {result.exit_code})")
            
            parsed = []
            errors = []
            if result.exit_code == 0:
                try:
                    parsed = plugin.parse(result.stdout, result.stderr)
                except Exception as e:
                    errors.append(f"Parse error: {str(e)}")
            else:
                errors.append(f"Execution failed with exit code {result.exit_code}")
            
            if result.error_message:
                errors.append(result.error_message)
                
            metadata = {}
            if result.exit_code == 0 and not errors:
                try:
                    metadata = plugin.build_metadata(parsed)
                    valid_keys = {"new_subdomains", "new_hosts", "new_urls", "new_js_files", "new_endpoints", "new_secrets", "new_swagger", "new_graphql", "new_nuclei", "new_dalfox", "new_takeovers", "new_fuzz_results", "new_findings"}
                    invalid_keys = [k for k in metadata.keys() if k not in valid_keys]
                    if invalid_keys:
                        errors.append(f"Invalid metadata keys returned by plugin: {invalid_keys}")
                        metadata = {}
                except Exception as e:
                    errors.append(f"Metadata build error: {str(e)}")

            success = result.success and len(errors) == 0
                
            tool_res = ToolResult(
                tool_name=plugin.metadata().name,
                plugin_version=plugin.metadata().version,
                binary_path=result.binary_path,
                command=result.command,
                working_directory=result.cwd,
                success=success,
                exit_code=result.exit_code,
                stdout=result.stdout,
                stderr=result.stderr,
                stdout_size=result.stdout_size,
                parsed_findings=len(parsed) if isinstance(parsed, list) else 0,
                errors=tuple(errors),
                error_message=result.error_message if result.error_message else None,
                execution_time=result.execution_time,
                parsed_output=tuple(parsed) if isinstance(parsed, list) else (parsed,),
                metadata_schema_version=METADATA_SCHEMA_VERSION,
                metadata=metadata
            )
            
            # Invariant: Parsed output is not lost if parsing was successful
            if success and parsed and not tool_res.parsed_output:
                logger.error(f"Invariant violation: Parsed output lost for {plugin.metadata().name}")

            results.append(tool_res)
            
        return tuple(results)
