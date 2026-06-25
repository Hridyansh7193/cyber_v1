from typing import Literal
from orchestrator.graph_state import GraphState

def planner_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("planner", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "recon_node"
    return "error_handler"

def recon_transition(state: GraphState) -> Literal["js_node", "error_handler"]:
    # The prompt explicitly specifies:
    # "if task_status['recon'] in {COMPLETED, FAILED}: goto_js()"
    status = state["orchestration_state"].task_status.get("recon")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "js_node"
    return "error_handler"

def js_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("js", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "api_node"
    return "error_handler"

def api_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("api", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "vulnerability_node"
    return "error_handler"

def vuln_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("vuln", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "analysis_node"
    return "error_handler"

def analysis_transition(state: GraphState) -> str:
    status = state["orchestration_state"].task_status.get("analysis", "PENDING")
    if status in {"COMPLETED", "FAILED", "CANCELLED"}:
        return "report_node"
    return "error_handler"
