import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.plugins.registry import REGISTRY
from orchestrator.wrapper_result_applier import (
    apply_recon_wrapper_result, apply_js_wrapper_result, 
    apply_api_wrapper_result, apply_vuln_wrapper_result,
    apply_parameter_wrapper_result
)
from schemas.tool_result import ToolResult
from schemas.state import ExecutionState, TargetState
from datetime import datetime, timezone

def generate_dummy_data(plugin_name):
    # Generating mock inputs with banner texts, valid JSON, invalid JSON, and raw strings
    stdout_lines = [
        "BANNER: BugHunter Scanner v1.0",
        "[INFO] Starting scan on target",
        '{"host": "api.example.com", "ip": "1.2.3.4"}',
        '{"url": "http://api.example.com", "technologies": ["Nginx", "WAF"]}',
        '{"type": "XSS", "poc": "<script>alert(1)</script>"}',
        'Malformed JSON { missing quotes }',
        "plain.example.com",
        "http://plain.example.com/api"
    ]
    return "\n".join(stdout_lines), "Some stderr text\nWarning: network timeout"

def main():
    print("# Baseline Audit Report\n")
    plugin_names = REGISTRY.list_plugins()
    plugins = {name: REGISTRY.get_plugin(name) for name in plugin_names}
    
    total_plugins = len(plugins)
    print(f"Total Plugins Found: {total_plugins}\n")
    
    baseline_table = "| Plugin | Received | Parsed | Stored | Reported | PASS |\n"
    baseline_table += "|--------|----------|--------|--------|----------|------|\n"
    
    base_state = ExecutionState(target=TargetState(domain="example.com", scope=[], session_id="test_session", start_time=datetime.now(timezone.utc)))
    
    for plugin_name, plugin in plugins.items():
        stdout, stderr = generate_dummy_data(plugin_name)
        
        # 1. Input Lines
        input_objects = len([line for line in stdout.splitlines() if line.strip()])
        
        # 2. Parsed Objects
        parsed = []
        try:
            parsed_result = plugin.parse(stdout, stderr)
            if isinstance(parsed_result, tuple) and len(parsed_result) == 2 and isinstance(parsed_result[1], list):
                parsed, parse_errors = parsed_result
            else:
                parsed = parsed_result
            
            if not isinstance(parsed, (list, tuple)):
                parsed = [parsed] if parsed else []
        except Exception as e:
            print(f"[{plugin_name}] PARSE EXCEPTION: {e}")
            parsed = []
            
        parsed_count = len(parsed)
        
        # 3. Build metadata
        metadata = {}
        try:
            metadata = plugin.build_metadata(parsed)
        except Exception as e:
            print(f"[{plugin_name}] METADATA EXCEPTION: {e}")
            
        stored_count = sum(len(v) for k, v in metadata.items() if isinstance(v, (list, tuple)) and k not in ["tech_stack", "waf_detected"])
        
        # 4. State Integration (Reported)
        tool_res = ToolResult(
            tool_name=plugin_name,
            success=True,
            exit_code=0,
            stdout=stdout,
            stderr=stderr,
            execution_time=1.0,
            parsed_output=tuple(parsed),
            metadata=metadata
        )
        
        new_state = base_state
        try:
            # We determine which applier to use based on plugin capability or just try them
            # For simplicity, we just look at what metadata keys it produced
            if "new_subdomains" in metadata or "new_hosts" in metadata or "new_urls" in metadata:
                new_state = apply_recon_wrapper_result(new_state, (tool_res,))
            if "new_js_files" in metadata or "new_endpoints" in metadata or "new_secrets" in metadata:
                new_state = apply_js_wrapper_result(new_state, (tool_res,))
            if "new_graphql" in metadata or "new_swagger" in metadata or "new_schemas" in metadata:
                new_state = apply_api_wrapper_result(new_state, (tool_res,))
            if "new_nuclei" in metadata or "new_dalfox" in metadata or "new_takeovers" in metadata or "new_fuzz_results" in metadata:
                new_state = apply_vuln_wrapper_result(new_state, (tool_res,))
            if "new_parameters" in metadata:
                new_state = apply_parameter_wrapper_result(new_state, (tool_res,))
        except Exception as e:
            print(f"[{plugin_name}] APPLIER EXCEPTION: {e}")
            
        # Count reported objects based on state changes
        reported_count = 0
        if new_state.recon_state != base_state.recon_state:
            reported_count += len(new_state.recon_state.subdomains) + len(new_state.recon_state.alive_hosts) + len(new_state.recon_state.urls)
        if new_state.js_state != base_state.js_state:
            reported_count += len(new_state.js_state.js_files) + len(new_state.js_state.endpoints) + len(new_state.js_state.secrets)
        if new_state.api_state != base_state.api_state:
            reported_count += len(new_state.api_state.swagger_urls) + len(new_state.api_state.graphql_urls) + len(new_state.api_state.endpoints) + len(new_state.api_state.schemas)
        if new_state.vuln_state != base_state.vuln_state:
            reported_count += len(new_state.vuln_state.nuclei_results) + len(new_state.vuln_state.dalfox_results) + len(new_state.vuln_state.takeovers) + len(new_state.vuln_state.fuzz_results)
            
        pass_status = "PASS" if input_objects >= parsed_count >= stored_count >= reported_count else "FAIL"
        
        # Checking for invariants violation (like storing raw strings when it should be parsed)
        if parsed_count > 0 and isinstance(parsed[0], str) and "BANNER" in parsed[0]:
            pass_status = "FAIL (Contaminated)"
            
        baseline_table += f"| {plugin_name} | {input_objects} | {parsed_count} | {stored_count} | {reported_count} | {pass_status} |\n"

    print(baseline_table)
    
if __name__ == "__main__":
    main()
