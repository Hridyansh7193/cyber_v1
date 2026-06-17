from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from typing import List, Dict, Any

def apply_recon_wrapper_result(state: ExecutionState, new_subdomains: List[str] = None, new_hosts: List[str] = None, new_urls: List[str] = None) -> ExecutionState:
    merged_subs = list(dict.fromkeys(state.recon_state.subdomains + (new_subdomains or [])))
    merged_hosts = list(dict.fromkeys(state.recon_state.alive_hosts + (new_hosts or [])))
    merged_urls = list(dict.fromkeys(state.recon_state.urls + (new_urls or [])))
    
    new_recon = ReconState(
        subdomains=merged_subs,
        alive_hosts=merged_hosts,
        urls=merged_urls,
        parameters=state.recon_state.parameters
    )
    return state.model_copy(update={"recon_state": new_recon})

def apply_js_wrapper_result(state: ExecutionState, new_js_files: List[str] = None, new_endpoints: List[str] = None) -> ExecutionState:
    merged_files = list(dict.fromkeys(state.js_state.js_files + (new_js_files or [])))
    merged_endpoints = list(dict.fromkeys(state.js_state.endpoints + (new_endpoints or [])))
    
    new_js = JSState(
        js_files=merged_files,
        endpoints=merged_endpoints,
        secrets=state.js_state.secrets
    )
    return state.model_copy(update={"js_state": new_js})

def apply_api_wrapper_result(state: ExecutionState, new_swagger: List[str] = None, new_graphql: List[str] = None) -> ExecutionState:
    merged_swagger = list(dict.fromkeys(state.api_state.swagger_urls + (new_swagger or [])))
    merged_graphql = list(dict.fromkeys(state.api_state.graphql_urls + (new_graphql or [])))
    
    new_api = APIState(
        swagger_urls=merged_swagger,
        graphql_urls=merged_graphql
    )
    return state.model_copy(update={"api_state": new_api})

def apply_vuln_wrapper_result(state: ExecutionState, new_nuclei: List[Dict] = None, new_dalfox: List[Dict] = None) -> ExecutionState:
    merged_nuclei = state.vuln_state.nuclei_results + (new_nuclei or [])
    merged_dalfox = state.vuln_state.dalfox_results + (new_dalfox or [])
    
    new_vuln = VulnerabilityState(
        nuclei_results=merged_nuclei,
        dalfox_results=merged_dalfox,
        takeovers=state.vuln_state.takeovers
    )
    return state.model_copy(update={"vuln_state": new_vuln})
