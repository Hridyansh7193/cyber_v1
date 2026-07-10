import os
import tempfile
from schemas import tool_result
from typing import Tuple, List, Any
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugins.registry import REGISTRY
from execution.plugins.base import ExecutionPlugin
from execution.utils.process_runner import ProcessRunner
from execution.constants import METADATA_SCHEMA_VERSION, ToolMetadata
import time
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
                    
            if binary_path.endswith('.py'):
                import sys
                final_command = [sys.executable, binary_path]
            else:
                final_command = [binary_path]
            
            # Auto-extract target from state if not provided
            current_target = target
            if current_target is None:
                eligibility = plugin.metadata().target_eligibility
                candidate_pool = set()
                
                if "domain" in eligibility:
                    candidate_pool.add(state.target.domain)
                if "subdomains" in eligibility and hasattr(state, "recon_state"):
                    candidate_pool.update(state.recon_state.subdomains)
                if "alive_hosts" in eligibility and hasattr(state, "recon_state"):
                    candidate_pool.update(state.recon_state.alive_hosts)
                if "urls" in eligibility and hasattr(state, "recon_state"):
                    candidate_pool.update(state.recon_state.urls)
                if "parameters" in eligibility and hasattr(state, "recon_state"):
                    candidate_pool.update(state.recon_state.parameters)
                if "js_files" in eligibility and hasattr(state, "js_state"):
                    candidate_pool.update(state.js_state.js_files)
                if "endpoints" in eligibility and hasattr(state, "js_state"):
                    candidate_pool.update(state.js_state.endpoints)
                    
                # If no specific eligibility is defined, fallback to sensible defaults
                if not eligibility:
                    if plugin.metadata().name in ["subfinder", "assetfinder", "gau"]:
                        candidate_pool.add(state.target.domain)
                    elif hasattr(state, "recon_state") and state.recon_state.alive_hosts:
                        candidate_pool.add(list(state.recon_state.alive_hosts)[0])
                    else:
                        candidate_pool.add(state.target.resolved_url or state.target.domain)

                # Filter pool using wrapper's smart target selection
                filtered_pool = [t for t in candidate_pool if plugin.is_candidate(t)]
                
                # Sort for deterministic execution
                if filtered_pool:
                    current_target = sorted(list(set(filtered_pool)))
                else:
                    current_target = None
            
            # If a list was resolved but it is empty, skip execution to prevent hanging tools
            if current_target is None or (isinstance(current_target, (list, tuple, set)) and not current_target):
                logger.info(f"Skipping {plugin.metadata().name}: no targets available.")
                continue
                
            original_target_list = current_target if isinstance(current_target, (list, tuple, set)) else [current_target]
            received_count = len(original_target_list)
            unique_targets = len(set(original_target_list))
            
            # ---------------------------------------------------------
            # Execution Budget Manager: Enforce target limits
            # ---------------------------------------------------------
            if hasattr(config, "execution_budget") and config.execution_budget:
                max_targets = config.execution_budget.max_targets_per_plugin
                if unique_targets > max_targets:
                    logger.warning(f"Plugin {plugin.metadata().name} received {unique_targets} targets, exceeding budget of {max_targets}. Truncating.")
                    original_target_list = list(set(original_target_list))[:max_targets]
                    unique_targets = max_targets
                    current_target = original_target_list if plugin.metadata().supports_multi_input else original_target_list
                    
            # Auth header injection
            if config.auth.headers:
                supported_auth_tools = {"httpx", "nuclei", "dalfox", "ffuf", "katana"}
                if plugin.metadata().name in supported_auth_tools:
                    for header in config.auth.headers:
                        final_command.extend(["-H", header])
            
            # For tools that can natively handle a list of targets (like nuclei with -l), pass the list.
            # Otherwise, iterate.
            native_multi = {"nuclei", "dalfox", "httpx", "subzy", "katana"}
            
            final_commands = []
            temp_path = None
            
            timeout_override = None
            if hasattr(config, "timeouts"):
                plugin_name = plugin.metadata().name
                if hasattr(config.timeouts, f"{plugin_name}_timeout"):
                    timeout_override = getattr(config.timeouts, f"{plugin_name}_timeout")
                elif hasattr(config.timeouts, "global_timeout"):
                    timeout_override = getattr(config.timeouts, "global_timeout")
            
            if isinstance(current_target, list) and plugin.metadata().name not in native_multi:
                for t in current_target:
                    cmd_args = plugin.build_command(state,
                        {
                            "tool_manager": state.runtime_context.tool_manager if state.runtime_context else None,
                            "wordlist_manager": state.runtime_context.wordlist_manager if state.runtime_context else None,
                            "config": config,
                        },
                        target=t
                    )
                    if cmd_args:
                        final_commands.append(list(final_command) + list(cmd_args))
            else:
                cmd_args = plugin.build_command(state,
                    {
                        "tool_manager": state.runtime_context.tool_manager if state.runtime_context else None,
                        "wordlist_manager": state.runtime_context.wordlist_manager if state.runtime_context else None,
                        "config": config,
                    },
                    target=current_target
                )
                if cmd_args:
                    final_commands.append(list(final_command) + list(cmd_args))
                    for arg in cmd_args:
                        if isinstance(arg, str) and (arg.startswith(tempfile.gettempdir()) or "/tmp" in arg):
                            if os.path.exists(arg):
                                temp_path = arg
                                break
            
            if not final_commands:
                logger.info(f"Skipping {plugin.metadata().name}: build_command returned empty arguments.")
                continue

            merged_stdout = ""
            merged_stderr = ""
            merged_exit = 0
            merged_time = 0.0
            last_cmd = ""
            
            total_commands = len(final_commands)
            plugin_start_time = time.time()
            
            # Phase 0 Instrumentation Logging (PRE-EXECUTION)
            logger.info("=" * 80)
            logger.info(f"Plugin: {plugin.metadata().name}")
            logger.info(f"Received Targets : {received_count}")
            logger.info(f"Unique Targets   : {unique_targets}")
            logger.info(f"Executed Targets : {total_commands}")
            logger.info("=" * 80)
            
            for idx, cmd in enumerate(final_commands, 1):
                cmd_start_time = time.time()
                elapsed_total = int(cmd_start_time - plugin_start_time)
                
                # Phase 0.5 Progress Update
                logger.info(f"[{plugin.metadata().name.upper()}] Target {idx} / {total_commands} | Elapsed: {elapsed_total}s")
                
                result = ProcessRunner.run(cmd, plugin.metadata().name, timeout=timeout_override)
                merged_stdout += result.stdout + "\n"
                if result.stderr:
                    merged_stderr += result.stderr + "\n"
                merged_exit = result.exit_code if result.exit_code != 0 else merged_exit
                merged_time += result.execution_time
                sanitized_cmd = [arg if not (isinstance(arg, str) and (arg.startswith(tempfile.gettempdir()) or "/tmp" in arg)) else "/tmp/target_list" for arg in cmd]
                last_cmd = " ".join(map(str, sanitized_cmd))
            
            avg_time = merged_time / total_commands if total_commands > 0 else 0
            # Phase 0 Instrumentation Logging (POST-EXECUTION)
            logger.info("=" * 80)
            logger.info(f"Plugin: {plugin.metadata().name} - FINISHED")
            logger.info(f"Runtime          : {merged_time:.2f} sec")
            logger.info(f"Average          : {avg_time:.2f} sec")
            logger.info("=" * 80)
            
            from execution.utils.process_runner import ProcessResult
            result = ProcessResult(exit_code=merged_exit, stdout=merged_stdout, stderr=merged_stderr, execution_time=merged_time, binary_path=binary_path, command=last_cmd, cwd=os.getcwd(), error_message="")

            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            logger.info(f"EXIT CODE : {result.exit_code}")
            logger.info("STDOUT:")
            logger.info(result.stdout)
            logger.info("STDERR:")
            logger.info(result.stderr)
            logger.info("=" * 80)
            # Evidence & Telemetry writing logic
            if state.target.session_id:
                target_str = state.target.domain
                
                # Standard evidence log appending
                evidence_dir = os.path.join("workspaces", target_str, "sessions", state.target.session_id, "evidence")
                os.makedirs(evidence_dir, exist_ok=True)
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
                    
                # Full telemetry directory logging
                telemetry_dir = os.path.join("workspaces", target_str, "sessions", state.target.session_id, "telemetry", plugin.metadata().name)
                os.makedirs(telemetry_dir, exist_ok=True)
                import json
                try:
                    with open(os.path.join(telemetry_dir, "stdout.txt"), "w", encoding="utf-8") as f:
                        f.write(result.stdout)
                    with open(os.path.join(telemetry_dir, "stderr.txt"), "w", encoding="utf-8") as f:
                        f.write(result.stderr)
                    with open(os.path.join(telemetry_dir, "execution.json"), "w", encoding="utf-8") as f:
                        json.dump({
                            "command": result.command,
                            "arguments": final_command,
                            "exit_code": result.exit_code,
                            "runtime": result.execution_time
                        }, f, indent=2)
                except Exception as e:
                    logger.error(f"Failed to write telemetry for {plugin.metadata().name}: {e}")
            
            parsed = []
            errors = []
            if result.exit_code == 0:
                try:
                    parsed_result = plugin.parse(result.stdout, result.stderr)
                    if isinstance(parsed_result, tuple) and len(parsed_result) == 2 and isinstance(parsed_result[1], list):
                        parsed, parse_errors = parsed_result
                        errors.extend(parse_errors)
                    else:
                        parsed = parsed_result
                except Exception as e:
                    errors.append(f"Parse error: {str(e)}")
            else:
                errors.append(f"Execution failed with exit code {result.exit_code}")
            
            if result.error_message:
                errors.append(result.error_message)
                
            if state.target.session_id:
                target_str = state.target.domain
                telemetry_dir = os.path.join("workspaces", target_str, "sessions", state.target.session_id, "telemetry", plugin.metadata().name)
                try:
                    with open(os.path.join(telemetry_dir, "parsed.json"), "w", encoding="utf-8") as f:
                        # Pydantic models might be in parsed, serialize cautiously
                        import json
                        def default_serializer(obj):
                            if hasattr(obj, "model_dump"): return obj.model_dump()
                            if hasattr(obj, "__dict__"): return obj.__dict__
                            return str(obj)
                        json.dump(parsed, f, indent=2, default=default_serializer)
                except Exception as e:
                    logger.error(f"Failed to serialize parsed.json: {e}")
                
            metadata = {}
            if result.exit_code == 0 and not errors:
                try:
                    metadata = plugin.build_metadata(parsed)
                    valid_keys = {"new_subdomains", "new_hosts", "new_urls", "new_js_files", "new_endpoints", "new_secrets", "new_swagger", "new_graphql", "new_nuclei", "new_dalfox", "new_takeovers", "new_fuzz_results", "new_findings", "tech_stack", "waf_detected", "new_schemas", "new_parameters"}
                    invalid_keys = [k for k in metadata.keys() if k not in valid_keys]
                    if invalid_keys:
                        errors.append(f"Invalid metadata keys returned by plugin: {invalid_keys}")
                        metadata = {}
                except Exception as e:
                    errors.append(f"Metadata build error: {str(e)}")

            parsed_tuple = tuple(parsed) if isinstance(parsed, (list, tuple)) else ((parsed,) if parsed else ())
            parsed_findings = len(parsed_tuple)
            
            if result.stdout_size > 0 and parsed_findings == 0 and not errors:
                errors.append("Stdout was not empty but 0 objects were parsed.")

            success = result.success and len(errors) == 0
                
            failure_category = None
            if not success:
                # Basic failure classification based on the errors array and exit code
                err_text = (" ".join(errors) + " " + result.stderr + " " + (result.error_message or "")).lower()
                if "timeout" in err_text or "timed out" in err_text:
                    failure_category = "TIMEOUT"
                elif "error: invalid input" in err_text or "usage:" in err_text or "flag provided but not defined" in err_text:
                    failure_category = "CLI"
                elif "network" in err_text or "connection" in err_text or "i/o timeout" in err_text or "ssl error" in err_text or "max retries" in err_text:
                    failure_category = "NETWORK"
                elif "parse" in err_text or "json" in err_text:
                    failure_category = "PARSER"
                elif result.exit_code == -2:
                    failure_category = "DEPENDENCY"
                else:
                    failure_category = "UNKNOWN"

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
                parsed_findings=parsed_findings,
                received_count=received_count,
                errors=tuple(errors),
                error_message=result.error_message if result.error_message else None,
                failure_category=failure_category,
                execution_time=result.execution_time,
                parsed_output=parsed_tuple,
                metadata_schema_version=METADATA_SCHEMA_VERSION,
                metadata=metadata
            )
            
            # Invariant: Parsed output is not lost if parsing was successful
            if success and parsed and not tool_res.parsed_output:
                logger.error(f"Invariant violation: Parsed output lost for {plugin.metadata().name}")

            results.append(tool_res)
            
        return tuple(results)
