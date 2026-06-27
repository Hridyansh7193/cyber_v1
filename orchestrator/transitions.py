from typing import Literal
from orchestrator.graph_state import GraphState
from langgraph.graph import END

def planner_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("planner", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "recon_node"
    return END

def recon_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("recon", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "js_node"
    return END

def js_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("js", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "api_node"
    return END

def api_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("api", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "vulnerability_node"
    return END

def vuln_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("vulnerability", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "analysis_node"
    return END

def analysis_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("analysis", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "report_node"
    return END
