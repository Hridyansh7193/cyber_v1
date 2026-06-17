from typing import Literal
from orchestrator.graph_state import GraphState

def recon_transition(state: GraphState) -> Literal["js_node", "END"]:
    # The prompt explicitly specifies:
    # "if task_status['recon'] in {COMPLETED, FAILED}: goto_js()"
    status = state["orchestration_state"].task_status.get("recon")
    if status in {"COMPLETED", "FAILED"}:
        return "js_node"
    return "END"

def js_transition(state: GraphState) -> Literal["api_node", "END"]:
    status = state["orchestration_state"].task_status.get("js")
    if status in {"COMPLETED", "FAILED"}:
        return "api_node"
    return "END"

def api_transition(state: GraphState) -> Literal["vulnerability_node", "END"]:
    status = state["orchestration_state"].task_status.get("api")
    if status in {"COMPLETED", "FAILED"}:
        return "vulnerability_node"
    return "END"

def vuln_transition(state: GraphState) -> Literal["analysis_node", "END"]:
    status = state["orchestration_state"].task_status.get("vuln")
    if status in {"COMPLETED", "FAILED"}:
        return "analysis_node"
    return "END"

def analysis_transition(state: GraphState) -> Literal["report_node", "END"]:
    status = state["orchestration_state"].task_status.get("analysis")
    if status in {"COMPLETED", "FAILED"}:
        return "report_node"
    return "END"
