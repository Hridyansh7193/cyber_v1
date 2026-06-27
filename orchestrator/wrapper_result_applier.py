from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from schemas.tool_result import ToolResult
from typing import Tuple

def apply_recon_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_subdomains = list(state.recon_state.subdomains)
    new_hosts = list(state.recon_state.alive_hosts)
    new_urls = list(state.recon_state.urls)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_subdomains.extend(output.get("new_subdomains", []))
        new_hosts.extend(output.get("new_hosts", []))
        new_urls.extend(output.get("new_urls", []))

    merged_subs = tuple(dict.fromkeys(new_subdomains))
    merged_hosts = tuple(dict.fromkeys(new_hosts))
    merged_urls = tuple(dict.fromkeys(new_urls))
    
    new_recon = ReconState(
        subdomains=merged_subs,
        alive_hosts=merged_hosts,
        urls=merged_urls,
        parameters=state.recon_state.parameters
    )
    return state.model_copy(deep=True, update={"recon_state": new_recon})

def apply_js_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_js_files = list(state.js_state.js_files)
    new_endpoints = list(state.js_state.endpoints)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_js_files.extend(output.get("new_js_files", []))
        new_endpoints.extend(output.get("new_endpoints", []))

    merged_files = tuple(dict.fromkeys(new_js_files))
    merged_endpoints = tuple(dict.fromkeys(new_endpoints))
    
    new_js = JSState(
        js_files=merged_files,
        endpoints=merged_endpoints,
        secrets=state.js_state.secrets
    )
    return state.model_copy(deep=True, update={"js_state": new_js})

def apply_api_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_swagger = list(state.api_state.swagger_urls)
    new_graphql = list(state.api_state.graphql_urls)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_swagger.extend(output.get("new_swagger", []))
        new_graphql.extend(output.get("new_graphql", []))

    merged_swagger = tuple(dict.fromkeys(new_swagger))
    merged_graphql = tuple(dict.fromkeys(new_graphql))
    
    new_api = APIState(
        swagger_urls=merged_swagger,
        graphql_urls=merged_graphql
    )
    return state.model_copy(deep=True, update={"api_state": new_api})

def apply_vuln_wrapper_result(state: ExecutionState, wrapper_out: Tuple[ToolResult, ...]) -> ExecutionState:
    new_nuclei = list(state.vuln_state.nuclei_results)
    new_dalfox = list(state.vuln_state.dalfox_results)
    
    for tool_res in wrapper_out:
        output = tool_res.metadata or {}
        new_nuclei.extend(output.get("new_nuclei", []))
        new_dalfox.extend(output.get("new_dalfox", []))
    
    new_vuln = VulnerabilityState(
        nuclei_results=tuple(new_nuclei),
        dalfox_results=tuple(new_dalfox),
        takeovers=state.vuln_state.takeovers
    )
    return state.model_copy(deep=True, update={"vuln_state": new_vuln})
