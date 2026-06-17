import pytest
from orchestrator.transitions import recon_transition, js_transition, api_transition, vuln_transition, analysis_transition
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.graph_state import GraphState

def test_recon_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"recon": "COMPLETED"}, errors={})}
    assert recon_transition(state) == "js_node"
    
    state["orchestration_state"].task_status["recon"] = "FAILED"
    assert recon_transition(state) == "js_node"
    
    state["orchestration_state"].task_status["recon"] = "CANCELLED"
    assert recon_transition(state) == "js_node"
    
    state["orchestration_state"].task_status["recon"] = "PENDING"
    assert recon_transition(state) == "error_handler"
    
    state["orchestration_state"].task_status["recon"] = "RUNNING"
    assert recon_transition(state) == "error_handler"

def test_js_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"js": "COMPLETED"}, errors={})}
    assert js_transition(state) == "api_node"
    
    state["orchestration_state"].task_status["js"] = "FAILED"
    assert js_transition(state) == "api_node"
    
    state["orchestration_state"].task_status["js"] = "CANCELLED"
    assert js_transition(state) == "api_node"
    
    state["orchestration_state"].task_status["js"] = "PENDING"
    assert js_transition(state) == "error_handler"

def test_api_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"api": "COMPLETED"}, errors={})}
    assert api_transition(state) == "vulnerability_node"
    
    state["orchestration_state"].task_status["api"] = "FAILED"
    assert api_transition(state) == "vulnerability_node"
    
    state["orchestration_state"].task_status["api"] = "CANCELLED"
    assert api_transition(state) == "vulnerability_node"
    
    state["orchestration_state"].task_status["api"] = "PENDING"
    assert api_transition(state) == "error_handler"

def test_vuln_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"vuln": "COMPLETED"}, errors={})}
    assert vuln_transition(state) == "analysis_node"
    
    state["orchestration_state"].task_status["vuln"] = "FAILED"
    assert vuln_transition(state) == "analysis_node"
    
    state["orchestration_state"].task_status["vuln"] = "CANCELLED"
    assert vuln_transition(state) == "analysis_node"
    
    state["orchestration_state"].task_status["vuln"] = "PENDING"
    assert vuln_transition(state) == "error_handler"

def test_analysis_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"analysis": "COMPLETED"}, errors={})}
    assert analysis_transition(state) == "report_node"
    
    state["orchestration_state"].task_status["analysis"] = "FAILED"
    assert analysis_transition(state) == "report_node"
    
    state["orchestration_state"].task_status["analysis"] = "CANCELLED"
    assert analysis_transition(state) == "report_node"
    
    state["orchestration_state"].task_status["analysis"] = "PENDING"
    assert analysis_transition(state) == "error_handler"
