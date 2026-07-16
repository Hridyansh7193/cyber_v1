import os
import json
import tempfile
import concurrent.futures
from typing import Tuple, List, Any
from schemas.tool_result import ToolResult
from config.schemas import BugHunterConfig
from execution.plugins.registry import REGISTRY
from execution.plugins.base import ExecutionPlugin
from execution.utils.process_runner import ProcessRunner
from execution.utils.timeout_manager import TimeoutManager
from execution.constants import (
    METADATA_SCHEMA_VERSION,
    NEW_SUBDOMAINS,
    NEW_HOSTS,
    NEW_URLS,
    NEW_PARAMETERS,
    NEW_JS_FILES,
    NEW_ENDPOINTS,
    NEW_SECRETS
)
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
                
                # Check eligibility categories in order of preference (priority fallback hierarchy)
                resolved_targets = []
                for elig_type in eligibility:
                    candidates = []
                    if elig_type == "domain":
                        # HTTPX is the first active probe.  Prefer the URL
                        # resolved by TargetResolver so a local target such as
                        # ``http://localhost:3000`` retains its scheme and
                        # port instead of being reduced to ``localhost:3000``.
                        if plugin.metadata().name == "httpx":
                            # Preserve an explicitly supplied scheme and port
                            # even if TargetResolver could not complete its
                            # preliminary HEAD request.
                            target_url = state.target.resolved_url
                            if not target_url and state.target.scheme:
                                target_url = f"{state.target.scheme}://{state.target.domain}"
                            candidates = [target_url] if target_url else [state.target.domain]
                        else:
                            candidates = [state.target.domain]
                    elif elig_type == "subdomains" and hasattr(state, "recon_state") and state.recon_state.subdomains:
                        candidates = list(state.recon_state.subdomains)
                    elif elig_type == "alive_hosts" and hasattr(state, "recon_state") and state.recon_state.alive_hosts:
                        candidates = list(state.recon_state.alive_hosts)
                    elif elig_type == "urls" and hasattr(state, "recon_state") and state.recon_state.urls:
                        candidates = list(state.recon_state.urls)
                    elif elig_type == "parameters" and hasattr(state, "recon_state") and state.recon_state.parameters:
                        candidates = []
                        for p in state.recon_state.parameters:
                            if isinstance(p, dict) and "url" in p and "parameters" in p:
                                url = p["url"]
                                sep = "&" if "?" in url else "?"
                                for param in p["parameters"]:
                                    candidates.append(f"{url}{sep}{param}=")
                            else:
                                candidates.append(str(p))
                    elif elig_type == "js_files" and hasattr(state, "js_state") and state.js_state.js_files:
                        candidates = list(state.js_state.js_files)
                    elif elig_type == "endpoints" and hasattr(state, "js_state") and state.js_state.endpoints:
                        base_url = state.target.resolved_url or (f"http://{state.target.domain}" if not state.target.domain.startswith("http") else state.target.domain)
                        base_url = base_url.rstrip("/")
                        candidates = []
                        for ep in state.js_state.endpoints:
                            if str(ep).startswith("/"):
                                candidates.append(f"{base_url}{ep}")
                            else:
                                candidates.append(str(ep))
                        
                    # Filter candidates using plugin.is_candidate
                    filtered = [c for c in candidates if plugin.is_candidate(c)]
                    if filtered:
                        resolved_targets = filtered
                        break  # Found the highest-priority eligible target list!
                
                if resolved_targets:
                    current_target = sorted(list(set(resolved_targets)))
                else:
                    # If no specific eligibility is defined, fallback to sensible defaults
                    if not eligibility:
                        candidate_pool = set()
                        if plugin.metadata().name in ["subfinder", "assetfinder", "gau"]:
                            candidate_pool.add(state.target.domain)
                        elif hasattr(state, "recon_state") and state.recon_state.alive_hosts:
                            candidate_pool.add(list(state.recon_state.alive_hosts)[0])
                        else:
                            candidate_pool.add(state.target.resolved_url or state.target.domain)
                        
                        filtered_pool = [t for t in candidate_pool if plugin.is_candidate(t)]
                        if filtered_pool:
                            current_target = sorted(list(set(filtered_pool)))
                        else:
                            current_target = None
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
            plugin_name = plugin.metadata().name
            
            heavy_tools = {"katana", "nuclei", "ffuf", "dalfox", "arjun"}
            if plugin_name in heavy_tools:
                heavy_cap = 10 if plugin_name == "arjun" else 100
                if unique_targets > heavy_cap:
                    logger.warning(f"Plugin {plugin_name} is a heavy tool. Capping targets from {unique_targets} to {heavy_cap}.")
                    original_target_list = list(set(original_target_list))[:heavy_cap]
                    unique_targets = heavy_cap
                    current_target = original_target_list if plugin.metadata().supports_multi_input else original_target_list

            if hasattr(config, "execution_budget") and config.execution_budget:
                max_targets = config.execution_budget.max_targets_per_plugin
                if unique_targets > max_targets:
                    logger.warning(f"Plugin {plugin_name} received {unique_targets} targets, exceeding budget of {max_targets}. Truncating.")
                    original_target_list = list(set(original_target_list))[:max_targets]
                    unique_targets = max_targets
                    current_target = original_target_list if plugin.metadata().supports_multi_input else original_target_list
                    
            # Chunk-Level Resume offsets
            offset_path = ""
            start_chunk_idx = 0
            if state.target.session_id:
                from utils.target_utils import sanitize_workspace_target
                offset_path = os.path.join("workspaces", sanitize_workspace_target(state.target.domain), "sessions", state.target.session_id, "plugin_offsets.json")
                if os.path.exists(offset_path):
                    try:
                        with open(offset_path, "r", encoding="utf-8") as f:
                            offsets = json.load(f)
                            start_chunk_idx = offsets.get(plugin_name, 0)
                            if start_chunk_idx > 0:
                                logger.info(f"Resuming {plugin_name} from chunk {start_chunk_idx}")
                    except Exception:
                        pass
                        
            chunk_size = 50
            if hasattr(config, "execution_budget") and hasattr(config.execution_budget, "chunk_size"):
                chunk_size = config.execution_budget.chunk_size
                
            max_workers = 1
            if hasattr(config, "execution_budget") and hasattr(config.execution_budget, "max_workers"):
                max_workers = config.execution_budget.max_workers
                
            target_chunks = [original_target_list[i:i + chunk_size] for i in range(0, len(original_target_list), chunk_size)]
            
            # Auth header injection
            if config.auth.headers:
                supported_auth_tools = {"httpx", "nuclei", "dalfox", "ffuf", "katana"}
                if plugin_name in supported_auth_tools:
                    for header in config.auth.headers:
                        final_command.extend(["-H", header])
            
            native_multi = {"nuclei", "dalfox", "httpx", "subzy", "katana", "arjun"}
            
            timeout_override = None
            if hasattr(config, "timeouts"):
                if hasattr(config.timeouts, f"{plugin_name}_timeout"):
                    timeout_override = getattr(config.timeouts, f"{plugin_name}_timeout")
                elif hasattr(config.timeouts, "global_timeout"):
                    timeout_override = getattr(config.timeouts, "global_timeout")
            
            merged_stdout = ""
            merged_stderr = ""
            merged_exit = 0
            merged_time = 0.0
            last_cmd = ""
            
            plugin_start_time = time.time()
            
            logger.info("=" * 80)
            logger.info(f"Plugin: {plugin_name}")
            logger.info(f"Received Targets : {received_count}")
            logger.info(f"Unique Targets   : {unique_targets}")
            logger.info(f"Total Chunks     : {len(target_chunks)}")
            if start_chunk_idx > 0:
                logger.info(f"Resuming From    : Chunk {start_chunk_idx}")
            logger.info("=" * 80)
            
            def process_command(cmd, idx, total, t_path=None):
                cmd_start_time = time.time()
                elapsed_total = int(cmd_start_time - plugin_start_time)
                logger.info(f"[{plugin_name.upper()}] Command {idx} / {total} | Elapsed: {elapsed_total}s")
                
                result = ProcessRunner.run(cmd, plugin_name, timeout=timeout_override)
                sanitized_cmd = [arg if not (isinstance(arg, str) and (arg.startswith(tempfile.gettempdir()) or "/tmp" in arg)) else "/tmp/target_list" for arg in cmd]
                cmd_str = " ".join(map(str, sanitized_cmd))
                
                if t_path:
                    try:
                        os.remove(t_path)
                    except OSError:
                        pass
                        
                return result, cmd_str

            for chunk_idx, chunk in enumerate(target_chunks):
                if chunk_idx < start_chunk_idx:
                    continue
                
                # Per-plugin runtime budget: abort if this plugin has been running too long
                plugin_elapsed = time.time() - plugin_start_time
                plugin_budget = timeout_override if timeout_override else TimeoutManager.get_timeout(plugin_name)
                # Give the plugin at most 2x its per-command timeout as total budget
                plugin_total_budget = plugin_budget * 2
                if plugin_elapsed > plugin_total_budget:
                    logger.warning(f"Plugin {plugin_name} exceeded total runtime budget ({int(plugin_elapsed)}s > {plugin_total_budget}s). Aborting remaining chunks.")
                    merged_stderr += f"Plugin {plugin_name} aborted: exceeded total runtime budget of {plugin_total_budget}s\n"
                    merged_exit = -1
                    break
                    
                final_commands = []
                temp_paths = []
                
                if plugin_name not in native_multi:
                    for t in chunk:
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
                            temp_paths.append(None)
                else:
                    cmd_args = plugin.build_command(state,
                        {
                            "tool_manager": state.runtime_context.tool_manager if state.runtime_context else None,
                            "wordlist_manager": state.runtime_context.wordlist_manager if state.runtime_context else None,
                            "config": config,
                        },
                        target=chunk
                    )
                    if cmd_args:
                        final_commands.append(list(final_command) + list(cmd_args))
                        t_path = None
                        for arg in cmd_args:
                            if isinstance(arg, str) and (arg.startswith(tempfile.gettempdir()) or "/tmp" in arg):
                                if os.path.exists(arg):
                                    t_path = arg
                                    break
                        temp_paths.append(t_path)
                        
                if not final_commands:
                    continue
                    
                total_commands = len(final_commands)
                
                try:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        futures = []
                        for i, cmd in enumerate(final_commands):
                            try:
                                futures.append(
                                    executor.submit(process_command, cmd, i+1, total_commands, temp_paths[i])
                                )
                            except RuntimeError as e:
                                # Interpreter shutdown or executor already closed
                                logger.warning(f"Could not submit command {i+1}/{total_commands} for {plugin_name}: {e}")
                                merged_stderr += f"Executor shutdown during {plugin_name}: {e}\n"
                                merged_exit = 1
                                break
                        for future in concurrent.futures.as_completed(futures):
                            try:
                                result, cmd_str = future.result()
                                merged_stdout += result.stdout + "\n"
                                if result.stderr:
                                    merged_stderr += result.stderr + "\n"
                                merged_exit = result.exit_code if result.exit_code != 0 else merged_exit
                                merged_time += result.execution_time
                                last_cmd = cmd_str
                            except Exception as e:
                                merged_stderr += f"Execution error: {e}\n"
                                merged_exit = 1
                except RuntimeError as e:
                    # Catch "cannot schedule new futures after interpreter shutdown"
                    logger.error(f"ThreadPoolExecutor RuntimeError for {plugin_name}: {e}")
                    merged_stderr += f"Executor shutdown: {e}\n"
                    merged_exit = 1
                    break
                
                # Save chunk offset
                if offset_path:
                    try:
                        os.makedirs(os.path.dirname(offset_path), exist_ok=True)
                        offsets = {}
                        if os.path.exists(offset_path):
                            with open(offset_path, "r", encoding="utf-8") as f:
                                offsets = json.load(f)
                        offsets[plugin_name] = chunk_idx + 1
                        with open(offset_path, "w", encoding="utf-8") as f:
                            json.dump(offsets, f)
                    except Exception as e:
                        logger.warning(f"Failed to save plugin offset: {e}")
                        
            from execution.utils.process_runner import ProcessResult
            result = ProcessResult(exit_code=merged_exit, stdout=merged_stdout, stderr=merged_stderr, execution_time=merged_time, binary_path=binary_path, command=last_cmd, cwd=os.getcwd(), error_message="")
            logger.info(f"EXIT CODE : {result.exit_code}")
            logger.info("STDOUT:")
            logger.info(result.stdout)
            logger.info("STDERR:")
            logger.info(result.stderr)
            logger.info("=" * 80)
            # Evidence & Telemetry writing logic
            if state.target.session_id:
                from utils.target_utils import sanitize_workspace_target
                target_str = sanitize_workspace_target(state.target.domain)
                
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
                    
                telemetry_dir = os.path.join("workspaces", target_str, "sessions", state.target.session_id, "telemetry", plugin_name)
                os.makedirs(telemetry_dir, exist_ok=True)
                try:
                    with open(os.path.join(telemetry_dir, "stdout.txt"), "w", encoding="utf-8") as f:
                        f.write(result.stdout)
                    with open(os.path.join(telemetry_dir, "stderr.txt"), "w", encoding="utf-8") as f:
                        f.write(result.stderr)
                    from execution.utils.redaction import redact_command_string, redact_command_list
                    with open(os.path.join(telemetry_dir, "execution.json"), "w", encoding="utf-8") as f:
                        json.dump({
                            "command": redact_command_string(result.command),
                            "arguments": redact_command_list(final_command),
                            "execution_args": final_command,
                            "exit_code": result.exit_code,
                            "runtime": result.execution_time,
                            # Keep the concise runner exception alongside the
                            # raw streams.  Raw API responses can be hundreds
                            # of kilobytes and otherwise obscure the reason a
                            # process returned a negative exit code.
                            "error_message": result.error_message,
                        }, f, indent=2)
                except Exception as e:
                    logger.error(f"Failed to write telemetry for {plugin_name}: {e}")
            
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
                from utils.target_utils import sanitize_workspace_target
                target_str = sanitize_workspace_target(state.target.domain)
                telemetry_dir = os.path.join("workspaces", target_str, "sessions", state.target.session_id, "telemetry", plugin_name)
                try:
                    with open(os.path.join(telemetry_dir, "parsed.json"), "w", encoding="utf-8") as f:
                        # Pydantic models might be in parsed, serialize cautiously
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
                # Several scanners emit progress, banner, or no-result status
                # lines on stdout.  A clean exit with no parseable findings is
                # a valid empty result, not an execution failure.
                logger.info(
                    f"{plugin.metadata().name} produced no parseable findings; "
                    "treating the successful command as an empty result."
                )

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

            from execution.utils.redaction import redact_command_string
            tool_res = ToolResult(
                tool_name=plugin.metadata().name,
                plugin_version=plugin.metadata().version,
                binary_path=result.binary_path,
                command=redact_command_string(result.command),
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
            
            # Apply the results of this plugin to the state dynamically,
            # so the next plugin in the loop can see the newly discovered targets!
            if tool_res.success and tool_res.metadata:
                output = tool_res.metadata
                if hasattr(state, "recon_state") and state.recon_state:
                    new_subdomains = list(state.recon_state.subdomains)
                    new_hosts = list(state.recon_state.alive_hosts)
                    new_urls = list(state.recon_state.urls)
                    new_params = list(state.recon_state.parameters)
                    merged_tech = dict(state.recon_state.tech_stack)
                    merged_waf = dict(state.recon_state.waf_detected)
                    
                    updated = False
                    if NEW_SUBDOMAINS in output:
                        new_subdomains.extend(output[NEW_SUBDOMAINS])
                        updated = True
                    if NEW_HOSTS in output:
                        new_hosts.extend(output[NEW_HOSTS])
                        updated = True
                    if NEW_URLS in output:
                        new_urls.extend(output[NEW_URLS])
                        updated = True
                    if NEW_PARAMETERS in output:
                        new_params.extend(output[NEW_PARAMETERS])
                        updated = True
                    if "tech_stack" in output:
                        for k, v in output["tech_stack"].items():
                            if k in merged_tech:
                                merged_tech[k] = tuple(dict.fromkeys(list(merged_tech[k]) + list(v)))
                            else:
                                merged_tech[k] = v
                        updated = True
                    if "waf_detected" in output:
                        merged_waf.update(output["waf_detected"])
                        updated = True
                        
                    if updated:
                        state = state.model_copy(update={
                            "recon_state": state.recon_state.model_copy(update={
                                "subdomains": tuple(dict.fromkeys(new_subdomains)),
                                "alive_hosts": tuple(dict.fromkeys(new_hosts)),
                                "urls": tuple(dict.fromkeys(new_urls)),
                                "parameters": tuple(dict.fromkeys(new_params)),
                                "tech_stack": merged_tech,
                                "waf_detected": merged_waf
                            })
                        })
                        
                if hasattr(state, "js_state") and state.js_state:
                    new_js_files = list(state.js_state.js_files)
                    new_endpoints = list(state.js_state.endpoints)
                    new_secrets = list(state.js_state.secrets)
                    
                    updated = False
                    if NEW_JS_FILES in output:
                        new_js_files.extend(output[NEW_JS_FILES])
                        updated = True
                    if NEW_ENDPOINTS in output:
                        new_endpoints.extend(output[NEW_ENDPOINTS])
                        updated = True
                    if NEW_SECRETS in output:
                        new_secrets.extend(output[NEW_SECRETS])
                        updated = True
                        
                    if updated:
                        seen_secrets = set()
                        merged_secrets = []
                        for s in new_secrets:
                            repr_str = str(sorted(s.items())) if isinstance(s, dict) else str(s)
                            if repr_str not in seen_secrets:
                                seen_secrets.add(repr_str)
                                merged_secrets.append(s)
                        state = state.model_copy(update={
                            "js_state": state.js_state.model_copy(update={
                                "js_files": tuple(dict.fromkeys(new_js_files)),
                                "endpoints": tuple(dict.fromkeys(new_endpoints)),
                                "secrets": tuple(merged_secrets)
                            })
                        })
            
        return tuple(results)
