import pytest
from orchestrator.transitions import recon_transition, js_transition, api_transition, vuln_transition, analysis_transition
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.graph_state import GraphState

def test_empty_findings_pipeline():
    # Construct a state where execution_state has empty findings
    # but orchestration_state has COMPLETED tasks.
    # Transitions must ONLY check task statuses, ignoring findings completely.
    orch_state = OrchestrationState(task_status={
        "recon": "COMPLETED",
        "js": "COMPLETED",
        "api": "COMPLETED",
        "vulnerability": "COMPLETED",
        "analysis": "COMPLETED"
    }, errors={})
    
    state: GraphState = {"execution_state": None, "orchestration_state": orch_state}
    
    assert recon_transition(state) == "js_node"
    assert js_transition(state) == "api_node"
    assert api_transition(state) == "vulnerability_node"
    assert vuln_transition(state) == "analysis_node"
    assert analysis_transition(state) == "report_node"
