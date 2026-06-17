from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from schemas.tool_result import ToolResult
from typing import List, Dict, Any

def apply_recon_wrapper_result(state: ExecutionState, wrapper_out: ToolResult) -> ExecutionState:
    output = wrapper_out.metadata or {}
    new_subdomains = output.get("new_subdomains", [])
    new_hosts = output.get("new_hosts", [])
    new_urls = output.get("new_urls", [])

    merged_subs = tuple(dict.fromkeys(state.recon_state.subdomains + tuple(new_subdomains)))
    merged_hosts = tuple(dict.fromkeys(state.recon_state.alive_hosts + tuple(new_hosts)))
    merged_urls = tuple(dict.fromkeys(state.recon_state.urls + tuple(new_urls)))
    
    new_recon = ReconState(
        subdomains=merged_subs,
        alive_hosts=merged_hosts,
        urls=merged_urls,
        parameters=state.recon_state.parameters
    )
    return state.model_copy(deep=True, update={"recon_state": new_recon})

def apply_js_wrapper_result(state: ExecutionState, wrapper_out: ToolResult) -> ExecutionState:
    output = wrapper_out.metadata or {}
    new_js_files = output.get("new_js_files", [])
    new_endpoints = output.get("new_endpoints", [])

    merged_files = tuple(dict.fromkeys(state.js_state.js_files + tuple(new_js_files)))
    merged_endpoints = tuple(dict.fromkeys(state.js_state.endpoints + tuple(new_endpoints)))
    
    new_js = JSState(
        js_files=merged_files,
        endpoints=merged_endpoints,
        secrets=state.js_state.secrets
    )
    return state.model_copy(deep=True, update={"js_state": new_js})

def apply_api_wrapper_result(state: ExecutionState, wrapper_out: ToolResult) -> ExecutionState:
    output = wrapper_out.metadata or {}
    new_swagger = output.get("new_swagger", [])
    new_graphql = output.get("new_graphql", [])

    merged_swagger = tuple(dict.fromkeys(state.api_state.swagger_urls + tuple(new_swagger)))
    merged_graphql = tuple(dict.fromkeys(state.api_state.graphql_urls + tuple(new_graphql)))
    
    new_api = APIState(
        swagger_urls=merged_swagger,
        graphql_urls=merged_graphql
    )
    return state.model_copy(deep=True, update={"api_state": new_api})

def apply_vuln_wrapper_result(state: ExecutionState, wrapper_out: ToolResult) -> ExecutionState:
    output = wrapper_out.metadata or {}
    new_nuclei = output.get("new_nuclei", [])
    new_dalfox = output.get("new_dalfox", [])

    merged_nuclei = state.vuln_state.nuclei_results + tuple(new_nuclei)
    merged_dalfox = state.vuln_state.dalfox_results + tuple(new_dalfox)
    
    new_vuln = VulnerabilityState(
        nuclei_results=merged_nuclei,
        dalfox_results=merged_dalfox,
        takeovers=state.vuln_state.takeovers
    )
    return state.model_copy(deep=True, update={"vuln_state": new_vuln})
