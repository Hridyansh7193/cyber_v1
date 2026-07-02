from typing import Tuple, List, Any
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugins.registry import REGISTRY
from execution.plugins.base import ExecutionPlugin
from execution.utils.process_runner import ProcessRunner
from execution.constants import METADATA_SCHEMA_VERSION, ToolMetadata
from utils.logger import get_logger

logger = get_logger("plugin_executor")

from schemas.state import ExecutionState

class PluginExecutor:
    """Handles the execution of plugins, enforcing validation."""
    
    @staticmethod
    def execute_plugins(plugin_names: Tuple[str, ...], config: BugHunterConfig, state: ExecutionState, target: Any = None) -> Tuple[ToolResult, ...]:
        results: List[ToolResult] = []
        
        for name in plugin_names:
            plugin: ExecutionPlugin = REGISTRY.get_plugin(name)
            if not plugin:
                continue
                
            if not plugin.validate(state, {}):
                continue
                
            # Retrieve Tool Binary
            tool_name = plugin.metadata().supported_tools[0]
            binary_path = tool_name
            tool_version = "unknown"
            
            if state.runtime_context and state.runtime_context.tool_manager:
                tool_info = state.runtime_context.tool_manager.get_tool(tool_name)
                if not tool_info:
                    logger.warning(f"Tool {tool_name} missing. Skipping {plugin.metadata().name}")
                    results.append(ToolResult(
                        tool_name=plugin.metadata().name,
                        plugin_version=plugin.metadata().version,
                        binary_path=tool_name,
                        command="",
                        success=False,
                        exit_code=-2,
                        stdout="",
                        stderr="",
                        errors=(f"Tool {tool_name} is missing or not installed.",),
                        error_message="Tool missing",
                        execution_time=0.0
                    ))
                    continue
                binary_path = tool_info.binary_path
                if tool_info.version:
                    tool_version = tool_info.version
                    
            final_command = [binary_path]
            
            # Auto-extract target from state if not provided
            current_target = target
            if current_target is None:
                if plugin.metadata().name in ["subfinder", "assetfinder", "gau"]:
                    current_target = state.target.domain
                elif plugin.metadata().name in ["httpx"]:
                    current_target = list(state.recon_state.subdomains) if state.recon_state.subdomains else state.target.domain
                elif plugin.metadata().name in ["katana"]:
                    current_target = list(state.recon_state.alive_hosts) if state.recon_state.alive_hosts else state.target.resolved_url or state.target.domain
                elif plugin.metadata().name in ["nuclei", "subzy", "ffuf"]:
                    # Vuln plugins act on URLs or endpoints
                    urls = set(state.recon_state.urls)
                    urls.update(state.js_state.endpoints)
                    urls.update(state.api_state.swagger_urls)
                    urls.update(state.api_state.graphql_urls)
                    current_target = list(urls) if urls else state.target.resolved_url or state.target.domain
                elif plugin.metadata().name == "dalfox":
                    # Dalfox should only target discovered parameters to minimize noise
                    current_target = list(state.recon_state.parameters) if state.recon_state.parameters else None
                else:
                    # Generic fallback
                    current_target = state.target.resolved_url or state.target.domain
            
            # Map plugin to its (single_target_flag, list_target_flag)
            flag_map = {
                "httpx": ("-u", "-l"),
                "nuclei": ("-u", "-l"),
                "katana": ("-u", "-list"),
                "subfinder": ("-d", "-dL"),
                "dalfox": ("url", "file"),
                "gau": (None, None),
                "assetfinder": (None, None),
                "subzy": ("--target", "--targets")
            }
            
            if current_target is not None and plugin.metadata().name in flag_map:
                import tempfile
                import os
                single_flag, list_flag = flag_map[plugin.metadata().name]
                
                if isinstance(current_target, (list, tuple, set)):
                    if list_flag:
                        fd, temp_path = tempfile.mkstemp(text=True)
                        with os.fdopen(fd, 'w') as f:
                            f.write("\n".join(current_target))
                        final_command.extend([list_flag, temp_path])
                    else:
                        # Fallback for tools that don't support lists natively (e.g. gau, assetfinder)
                        # but we still want to run them. We would need a wrapper loop, but for now we just use the first item.
                        if current_target:
                            if single_flag:
                                final_command.extend([single_flag, str(current_target[0])])
                            else:
                                final_command.append(str(current_target[0]))
                else:
                    if single_flag:
                        final_command.extend([single_flag, str(current_target)])
                    else:
                        final_command.append(str(current_target))
                        
            # Wordlist handling inside PluginExecutor
            if plugin.metadata().name == "ffuf" and state.runtime_context and state.runtime_context.wordlist_manager:
                wordlist_path = state.runtime_context.wordlist_manager.get("common")
                if wordlist_path:
                    final_command.extend(["-w", wordlist_path])
                else:
                    logger.warning("FFUF missing wordlist. Skipping.")
                    continue
            # Auth header injection
            if config.auth.headers:
                supported_auth_tools = {"httpx", "nuclei", "dalfox", "ffuf", "katana"}
                if plugin.metadata().name in supported_auth_tools:
                    for header in config.auth.headers:
                        final_command.extend(["-H", header])
            
            # Execute
            command = plugin.build_command(state, {})
            final_command.extend(command)
            logger.info(f"{plugin.metadata().name} started")
            result = ProcessRunner.run(final_command, plugin.metadata().name)
            logger.info(f"{plugin.metadata().name} finished in {result.execution_time:.2f}s (Exit code: {result.exit_code})")
            
            # Evidence writing logic
            if state.target.session_id:
                # We need to construct the path to evidence dir
                # Since WorkspaceService isn't passed here directly, we rely on a standard path format
                # assuming target and session_id exist
                target_str = state.target.domain
                import os
                evidence_dir = os.path.join("workspaces", target_str, "sessions", state.target.session_id, "evidence")
                if os.path.exists(evidence_dir):
                    stdout_file = os.path.join(evidence_dir, f"{plugin.metadata().name}_stdout.log")
                    stderr_file = os.path.join(evidence_dir, f"{plugin.metadata().name}_stderr.log")
                    try:
                        if result.stdout:
                            with open(stdout_file, "a", encoding="utf-8") as f:
                                f.write(result.stdout + "\n")
                        if result.stderr:
                            with open(stderr_file, "a", encoding="utf-8") as f:
                                f.write(result.stderr + "\n")
                    except Exception as e:
                        logger.error(f"Failed to write evidence for {plugin.metadata().name}: {e}")
            
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
                    valid_keys = {"new_subdomains", "new_hosts", "new_urls", "new_js_files", "new_endpoints", "new_secrets", "new_swagger", "new_graphql", "new_nuclei", "new_dalfox", "new_takeovers", "new_fuzz_results", "new_findings", "tech_stack", "waf_detected"}
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
