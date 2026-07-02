from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from schemas.tool_result import ToolResult
from schemas.telemetry import ExecutionTelemetry
from execution.constants import *
from typing import Tuple, List, Mapping, Any

def _extract_telemetry(wrapper_out: Tuple[ToolResult, ...]) -> Tuple[ExecutionTelemetry, ...]:
    return tuple(
        ExecutionTelemetry(
            tool=t.tool_name,
            version=t.plugin_version,
            command=t.command,
            execution_time=t.execution_time,
            exit_code=t.exit_code,
            stdout_size=t.stdout_size,
            stderr_size=len(t.stderr),
            parsed_objects=t.parsed_findings,
            success=t.success,
            timeout=t.exit_code == -1,
            wrapper_errors=tuple([e for e in t.errors if "Parse error" not in e]),
            parser_errors=tuple([e for e in t.errors if "Parse error" in e]),
            binary_path=t.binary_path,
            working_directory=t.working_directory
        )
        for t in wrapper_out
    )

def apply_recon_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_subdomains = list(state.recon_state.subdomains)
    new_hosts = list(state.recon_state.alive_hosts)
    new_urls = list(state.recon_state.urls)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    merged_tech = dict(state.recon_state.tech_stack)
    merged_waf = dict(state.recon_state.waf_detected)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_subdomains.extend(output.get(NEW_SUBDOMAINS, []))
        new_hosts.extend(output.get(NEW_HOSTS, []))
        new_urls.extend(output.get(NEW_URLS, []))
        
        # Merge tech stack
        for k, v in output.get("tech_stack", {}).items():
            if k in merged_tech:
                merged_tech[k] = tuple(dict.fromkeys(list(merged_tech[k]) + list(v)))
            else:
                merged_tech[k] = v
                
        # Merge waf detected
        merged_waf.update(output.get("waf_detected", {}))

    merged_subs = tuple(dict.fromkeys(new_subdomains))
    merged_hosts = tuple(dict.fromkeys(new_hosts))
    merged_urls = tuple(dict.fromkeys(new_urls))
    
    new_recon = ReconState(
        subdomains=merged_subs,
        alive_hosts=merged_hosts,
        urls=merged_urls,
        parameters=state.recon_state.parameters,
        tech_stack=merged_tech,
        waf_detected=merged_waf
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"recon_state": new_recon, "logs": tuple(new_logs)})

def apply_js_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_js_files = list(state.js_state.js_files)
    new_endpoints = list(state.js_state.endpoints)
    new_secrets = list(state.js_state.secrets)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_js_files.extend(output.get(NEW_JS_FILES, []))
        new_endpoints.extend(output.get(NEW_ENDPOINTS, []))
        
        # JS plugins like SecretFinder or Trufflehog might return secrets
        secrets = output.get(NEW_SECRETS, [])
        if secrets:
            new_secrets.extend(secrets)

    merged_files = tuple(dict.fromkeys(new_js_files))
    merged_endpoints = tuple(dict.fromkeys(new_endpoints))
    
    # Simple deduplication for secrets assuming they are dicts
    seen_secrets = set()
    merged_secrets = []
    for secret in new_secrets:
        # Create a hashable representation for deduplication
        # fallback to raw string representation if needed
        repr_str = str(sorted(secret.items())) if isinstance(secret, dict) else str(secret)
        if repr_str not in seen_secrets:
            seen_secrets.add(repr_str)
            merged_secrets.append(secret)
    
    new_js = JSState(
        js_files=merged_files,
        endpoints=merged_endpoints,
        secrets=tuple(merged_secrets)
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"js_state": new_js, "logs": tuple(new_logs)})

def apply_api_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_swagger = list(state.api_state.swagger_urls)
    new_graphql = list(state.api_state.graphql_urls)
    new_endpoints = list(state.api_state.endpoints)
    new_schemas = list(state.api_state.schemas)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_swagger.extend(output.get(NEW_SWAGGER, []))
        new_graphql.extend(output.get(NEW_GRAPHQL, []))
        new_endpoints.extend(output.get("new_endpoints", []))
        new_schemas.extend(output.get("new_schemas", []))

    merged_swagger = tuple(dict.fromkeys(new_swagger))
    merged_graphql = tuple(dict.fromkeys(new_graphql))
    
    # Deduplicate dicts
    seen_endpoints = set()
    merged_endpoints = []
    for ep in new_endpoints:
        repr_str = str(sorted(ep.items())) if isinstance(ep, dict) else str(ep)
        if repr_str not in seen_endpoints:
            seen_endpoints.add(repr_str)
            merged_endpoints.append(ep)
            
    seen_schemas = set()
    merged_schemas = []
    for schema in new_schemas:
        repr_str = str(sorted(schema.items())) if isinstance(schema, dict) else str(schema)
        if repr_str not in seen_schemas:
            seen_schemas.add(repr_str)
            merged_schemas.append(schema)
            
    new_api = APIState(
        swagger_urls=merged_swagger,
        graphql_urls=merged_graphql,
        endpoints=tuple(merged_endpoints),
        schemas=tuple(merged_schemas)
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"api_state": new_api, "logs": tuple(new_logs)})

def apply_vuln_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_nuclei = list(state.vuln_state.nuclei_results)
    new_dalfox = list(state.vuln_state.dalfox_results)
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_nuclei.extend(output.get(NEW_NUCLEI, []))
        new_dalfox.extend(output.get(NEW_DALFOX, []))
    
    new_vuln = VulnerabilityState(
        nuclei_results=tuple(new_nuclei),
        dalfox_results=tuple(new_dalfox),
        takeovers=state.vuln_state.takeovers
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"vuln_state": new_vuln, "logs": tuple(new_logs)})

def apply_parameter_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_logs = list(state.logs) + list(_extract_telemetry(wrapper_out))
    
    new_params = list(state.recon_state.parameters)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_params.extend(output.get("new_fuzz_results", []))

    merged_params = tuple(dict.fromkeys(new_params))
    
    new_recon = ReconState(
        subdomains=state.recon_state.subdomains,
        alive_hosts=state.recon_state.alive_hosts,
        urls=state.recon_state.urls,
        parameters=merged_params,
        tech_stack=state.recon_state.tech_stack,
        waf_detected=state.recon_state.waf_detected
    )
    
    assert len(new_logs) == len(state.logs) + len(wrapper_out), "Invariant violated: Telemetry count did not increase correctly"
    
    return state.model_copy(deep=True, update={"recon_state": new_recon, "logs": tuple(new_logs)})
