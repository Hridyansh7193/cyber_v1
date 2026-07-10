from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from agents.deltas import ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, FindingDelta, TaskQueueDelta, ReportDelta, IntelligenceDelta
from schemas.finding import Finding
import uuid

def apply_recon_delta(state: ExecutionState, delta: ReconDelta) -> ExecutionState:
    merged_tech = dict(state.recon_state.tech_stack)
    for k, v in delta.tech_stack.items():
        if k in merged_tech:
            merged_tech[k] = tuple(dict.fromkeys(list(merged_tech[k]) + list(v)))
        else:
            merged_tech[k] = v
            
    merged_waf = dict(state.recon_state.waf_detected)
    merged_waf.update(delta.waf_detected)

    new_recon = ReconState(
        subdomains=tuple(dict.fromkeys(list(state.recon_state.subdomains) + list(delta.subdomains))),
        alive_hosts=tuple(dict.fromkeys(list(state.recon_state.alive_hosts) + list(delta.alive_hosts))),
        urls=tuple(dict.fromkeys(list(state.recon_state.urls) + list(delta.urls))),
        parameters=state.recon_state.parameters,
        tech_stack=merged_tech,
        waf_detected=merged_waf
    )
    assert len(new_recon.subdomains) >= len(state.recon_state.subdomains), "Invariant violated: Subdomains lost during delta apply"
    assert len(new_recon.alive_hosts) >= len(state.recon_state.alive_hosts), "Invariant violated: Hosts lost during delta apply"
    assert len(new_recon.urls) >= len(state.recon_state.urls), "Invariant violated: URLs lost during delta apply"
    return state.model_copy(deep=True, update={"recon_state": new_recon})

def apply_js_delta(state: ExecutionState, delta: JSDelta) -> ExecutionState:
    new_js = JSState(
        js_files=tuple(dict.fromkeys(list(state.js_state.js_files) + list(delta.js_files))),
        endpoints=tuple(dict.fromkeys(list(state.js_state.endpoints) + list(delta.endpoints))),
        secrets=state.js_state.secrets
    )
    assert len(new_js.js_files) >= len(state.js_state.js_files), "Invariant violated: JS files lost during delta apply"
    assert len(new_js.endpoints) >= len(state.js_state.endpoints), "Invariant violated: Endpoints lost during delta apply"
    return state.model_copy(deep=True, update={"js_state": new_js})

def apply_api_delta(state: ExecutionState, delta: APIDelta) -> ExecutionState:
    new_api = APIState(
        swagger_urls=tuple(dict.fromkeys(list(state.api_state.swagger_urls) + list(delta.swagger_urls))),
        graphql_urls=tuple(dict.fromkeys(list(state.api_state.graphql_urls) + list(delta.graphql_urls)))
    )
    assert len(new_api.swagger_urls) >= len(state.api_state.swagger_urls), "Invariant violated: Swagger URLs lost during delta apply"
    assert len(new_api.graphql_urls) >= len(state.api_state.graphql_urls), "Invariant violated: GraphQL URLs lost during delta apply"
    return state.model_copy(deep=True, update={"api_state": new_api})

def apply_vulnerability_delta(state: ExecutionState, delta: VulnerabilityDelta) -> ExecutionState:
    existing_findings = {f.id: f for f in state.findings}
    for f_dict in delta.findings:
        finding = Finding(
            id=f_dict.get('id', ''),
            title=f_dict.get('title', 'Vulnerability'),
            severity=f_dict.get('severity', 'info'),
            confidence=f_dict.get('confidence', 'certain'),
            evidence=f_dict.get('evidence', ''),
            references=tuple(f_dict.get('references', []))
        )
        existing_findings[finding.id] = finding
    return state.model_copy(deep=True, update={"findings": tuple(existing_findings.values())})

def apply_finding_delta(state: ExecutionState, delta: FindingDelta) -> ExecutionState:
    existing_findings = {f.id: f for f in state.findings}
    for finding in delta.findings:
        existing_findings[finding.id] = finding
    return state.model_copy(deep=True, update={"findings": tuple(existing_findings.values())})

def apply_task_queue_delta(state: ExecutionState, delta: TaskQueueDelta) -> ExecutionState:
    from schemas.task import Task
    merged = list(state.task_queue)
    # Just append new tasks for now (simple logic)
    merged.extend(delta.task_queue)
    return state.model_copy(deep=True, update={"task_queue": tuple(merged)})

def apply_report_delta(state: ExecutionState, delta: ReportDelta) -> ExecutionState:
    new_reports = tuple(state.reports) + tuple(delta.reports)
    return state.model_copy(deep=True, update={"reports": new_reports})

def apply_intelligence_delta(state: ExecutionState, delta: IntelligenceDelta) -> ExecutionState:
    if not state.intelligence:
        return state.model_copy(deep=True, update={"intelligence": delta.intelligence})
    
    updates = {}
    if delta.intelligence.prioritized_assets:
        updates["prioritized_assets"] = delta.intelligence.prioritized_assets
    if delta.intelligence.correlated_findings:
        updates["correlated_findings"] = delta.intelligence.correlated_findings
    if delta.intelligence.attack_graph is not None:
        updates["attack_graph"] = delta.intelligence.attack_graph
    if delta.intelligence.risk_summary is not None:
        updates["risk_summary"] = delta.intelligence.risk_summary
        
    new_intelligence = state.intelligence.model_copy(deep=True, update=updates)
    return state.model_copy(deep=True, update={"intelligence": new_intelligence})
