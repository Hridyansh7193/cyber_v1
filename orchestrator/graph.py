from langgraph.graph import StateGraph, END
from orchestrator.graph_state import GraphState
from orchestrator.state_adapter import from_graph_state, to_graph_state
from orchestrator.nodes import init_node, recon_node, js_node, api_node, vulnerability_node, analysis_node, report_node
from orchestrator.transitions import recon_transition, js_transition, api_transition, vuln_transition, analysis_transition
from orchestrator.retry_policy import get_retry_policy
from orchestrator.checkpoint_manager import CheckpointManager
from config.schemas import BugHunterConfig

def build_graph(config: BugHunterConfig, checkpointer: CheckpointManager = None):
    workflow = StateGraph(GraphState)
    
    # We must wrap nodes to adapt GraphState <-> NodeResult
    def wrap_node(node_func, task_name=None):
        def wrapper(state: GraphState):
            result = from_graph_state(state)
            new_result = node_func(result, config)
            return to_graph_state(new_result)
        return wrapper

    retry = get_retry_policy()

    workflow.add_node("init_node", wrap_node(init_node), retry=retry)
    workflow.add_node("recon_node", wrap_node(recon_node), retry=retry)
    workflow.add_node("js_node", wrap_node(js_node), retry=retry)
    workflow.add_node("api_node", wrap_node(api_node), retry=retry)
    workflow.add_node("vulnerability_node", wrap_node(vulnerability_node), retry=retry)
    workflow.add_node("analysis_node", wrap_node(analysis_node), retry=retry)
    workflow.add_node("report_node", wrap_node(report_node), retry=retry)

    workflow.set_entry_point("init_node")
    workflow.add_edge("init_node", "recon_node")
    
    workflow.add_conditional_edges("recon_node", recon_transition, {"js_node": "js_node", "END": END})
    workflow.add_conditional_edges("js_node", js_transition, {"api_node": "api_node", "END": END})
    workflow.add_conditional_edges("api_node", api_transition, {"vulnerability_node": "vulnerability_node", "END": END})
    workflow.add_conditional_edges("vulnerability_node", vuln_transition, {"analysis_node": "analysis_node", "END": END})
    workflow.add_conditional_edges("analysis_node", analysis_transition, {"report_node": "report_node", "END": END})
    workflow.add_edge("report_node", END)

    saver = checkpointer.get_saver() if checkpointer else None
    return workflow.compile(checkpointer=saver)
