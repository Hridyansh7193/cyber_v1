import pytest
from orchestrator.transitions import passive_recon_transition, js_transition, api_transition, vuln_transition, analysis_transition
from orchestrator.orchestration_state import OrchestrationState
from orchestrator.graph_state import GraphState
from langgraph.graph import END

def test_passive_recon_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"passive_recon": "COMPLETED"}, errors={})}
    assert passive_recon_transition(state) == "scope_enforcement_node"
    
    state["orchestration_state"].task_status["passive_recon"] = "FAILED"
    assert passive_recon_transition(state) == "scope_enforcement_node"
    
    state["orchestration_state"].task_status["passive_recon"] = "CANCELLED"
    assert passive_recon_transition(state) == "scope_enforcement_node"
    
    state["orchestration_state"].task_status["passive_recon"] = "PENDING"
    assert passive_recon_transition(state) == END
    
    state["orchestration_state"].task_status["passive_recon"] = "RUNNING"
    assert passive_recon_transition(state) == END

def test_js_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"js": "COMPLETED"}, errors={})}
    assert js_transition(state) == "api_node"
    
    state["orchestration_state"].task_status["js"] = "FAILED"
    assert js_transition(state) == "api_node"
    
    state["orchestration_state"].task_status["js"] = "CANCELLED"
    assert js_transition(state) == "api_node"
    
    state["orchestration_state"].task_status["js"] = "PENDING"
    assert js_transition(state) == END

def test_api_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"api": "COMPLETED"}, errors={})}
    assert api_transition(state) == "parameter_node"
    
    state["orchestration_state"].task_status["api"] = "FAILED"
    assert api_transition(state) == "parameter_node"
    
    state["orchestration_state"].task_status["api"] = "CANCELLED"
    assert api_transition(state) == "parameter_node"
    
    state["orchestration_state"].task_status["api"] = "PENDING"
    assert api_transition(state) == END

def test_vuln_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"vulnerability": "COMPLETED"}, errors={})}
    assert vuln_transition(state) == "analysis_node"
    
    state["orchestration_state"].task_status["vulnerability"] = "FAILED"
    assert vuln_transition(state) == "analysis_node"
    
    state["orchestration_state"].task_status["vulnerability"] = "CANCELLED"
    assert vuln_transition(state) == "analysis_node"
    
    state["orchestration_state"].task_status["vulnerability"] = "PENDING"
    assert vuln_transition(state) == END

def test_analysis_transition():
    state: GraphState = {"execution_state": None, "orchestration_state": OrchestrationState(task_status={"analysis": "COMPLETED"}, errors={})}
    assert analysis_transition(state) == "report_node"
    
    state["orchestration_state"].task_status["analysis"] = "FAILED"
    assert analysis_transition(state) == "report_node"
    
    state["orchestration_state"].task_status["analysis"] = "CANCELLED"
    assert analysis_transition(state) == "report_node"
    
    state["orchestration_state"].task_status["analysis"] = "PENDING"
    assert analysis_transition(state) == END
