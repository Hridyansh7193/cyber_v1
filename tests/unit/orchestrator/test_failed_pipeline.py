import pytest
from orchestrator.transitions import passive_recon_transition, js_transition, api_transition, vuln_transition, analysis_transition
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.graph_state import GraphState

def test_failed_tasks_reach_report():
    orch_state = OrchestrationState(task_status={
        "passive_recon": "FAILED",
        "js": "FAILED",
        "api": "FAILED",
        "vulnerability": "FAILED",
        "analysis": "FAILED"
    }, errors={})
    
    state: GraphState = {"execution_state": None, "orchestration_state": orch_state}
    
    assert passive_recon_transition(state) == "scope_enforcement_node"
    assert js_transition(state) == "api_node"
    assert api_transition(state) == "parameter_node"
    assert vuln_transition(state) == "analysis_node"
    assert analysis_transition(state) == "report_node"
