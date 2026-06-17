from schemas.state import ExecutionState, ReconState, JSState, APIState, VulnerabilityState
from agents.deltas import ReconDelta, JSDelta, APIDelta, VulnerabilityDelta, AnalysisDelta, ReportDelta
from schemas.finding import Finding
import uuid

def apply_recon_delta(state: ExecutionState, delta: ReconDelta) -> ExecutionState:
    new_recon = ReconState(
        subdomains=list(delta.subdomains),
        alive_hosts=list(delta.alive_hosts),
        urls=list(delta.urls),
        parameters=state.recon_state.parameters
    )
    return state.model_copy(deep=True, update={"recon_state": new_recon})

def apply_js_delta(state: ExecutionState, delta: JSDelta) -> ExecutionState:
    new_js = JSState(
        js_files=list(delta.js_files),
        endpoints=list(delta.endpoints),
        secrets=state.js_state.secrets
    )
    return state.model_copy(deep=True, update={"js_state": new_js})

def apply_api_delta(state: ExecutionState, delta: APIDelta) -> ExecutionState:
    new_api = APIState(
        swagger_urls=list(delta.swagger_urls),
        graphql_urls=list(delta.graphql_urls)
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
    return state.model_copy(deep=True, update={"findings": new_findings})

def apply_report_delta(state: ExecutionState, delta: ReportDelta) -> ExecutionState:
    # Overwrite or append reports
    new_reports = list(state.reports) + list(delta.reports)
    return state.model_copy(deep=True, update={"reports": new_reports})
