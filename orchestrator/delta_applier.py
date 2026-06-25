from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from agents.deltas import ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, AnalysisDelta, ReportDelta, IntelligenceDelta
from schemas.finding import Finding
import uuid

def apply_recon_delta(state: ExecutionState, delta: ReconDelta) -> ExecutionState:
    new_recon = ReconState(
        subdomains=tuple(delta.subdomains),
        alive_hosts=tuple(delta.alive_hosts),
        urls=tuple(delta.urls),
        parameters=state.recon_state.parameters
    )
    return state.model_copy(deep=True, update={"recon_state": new_recon})

def apply_js_delta(state: ExecutionState, delta: JSDelta) -> ExecutionState:
    new_js = JSState(
        js_files=tuple(delta.js_files),
        endpoints=tuple(delta.endpoints),
        secrets=state.js_state.secrets
    )
    return state.model_copy(deep=True, update={"js_state": new_js})

def apply_api_delta(state: ExecutionState, delta: APIDelta) -> ExecutionState:
    new_api = APIState(
        swagger_urls=tuple(delta.swagger_urls),
        graphql_urls=tuple(delta.graphql_urls)
    )
    return state.model_copy(deep=True, update={"api_state": new_api})

def apply_vulnerability_delta(state: ExecutionState, delta: VulnerabilityDelta) -> ExecutionState:
    # Overwrite vulnerabilities as per agent's deduplicated output
    # But we don't map findings directly here unless Analysis phase.
    # We update the raw lists based on delta. (Actually Delta only provides findings dict).
    return state

def apply_analysis_delta(state: ExecutionState, delta: AnalysisDelta) -> ExecutionState:
    # Convert grouped findings to actual Finding objects
    new_findings = list(state.findings)
    for group in delta.grouped_findings:
        finding = Finding(
            id=str(uuid.uuid4()),
            title="Associated Endpoint",
            description=f"Endpoint {group.get('endpoint')} associated with {group.get('subdomains')}",
            severity="info",
            confidence="certain",
            metadata=group,
            evidence="Inferred via analysis node"
        )
        new_findings.append(finding)
    return state.model_copy(deep=True, update={"findings": tuple(new_findings)})

def apply_report_delta(state: ExecutionState, delta: ReportDelta) -> ExecutionState:
    # Overwrite or append reports
    new_reports = tuple(state.reports) + tuple(delta.reports)
    return state.model_copy(deep=True, update={"reports": new_reports})

def apply_intelligence_delta(state: ExecutionState, delta: IntelligenceDelta) -> ExecutionState:
    if not state.intelligence:
        return state.model_copy(deep=True, update={"intelligence": delta.intelligence})
    
    # Merge existing intelligence state with incoming delta, overriding fields that are not None
    # or appending tuples. The delta's intelligence acts as a patch.
    updates = {}
    if delta.intelligence.planner is not None:
        updates["planner"] = delta.intelligence.planner
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
