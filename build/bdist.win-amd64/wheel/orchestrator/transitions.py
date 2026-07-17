from orchestrator.graph_state import GraphState
from langgraph.graph import END
from utils.logger import get_logger

logger = get_logger("transitions")

# Terminal statuses that mean a node finished (successfully or not) and the pipeline should advance.
# CANCELLED explicitly stops the scan at that point.
# RUNNING/PENDING means the node never completed — this is a bug we log and halt on.
_ADVANCE_STATUSES = {"COMPLETED", "FAILED"}
_HALT_STATUSES = {"CANCELLED"}


def _transition(state: GraphState, task_key: str, next_node: str) -> str:
    """
    Generic transition helper.
    - COMPLETED or FAILED  -> advance to next_node (FAILED is non-fatal for the pipeline)
    - CANCELLED            -> END (user-requested stop)
    - RUNNING/PENDING/etc  -> END with a warning (node did not complete properly)
    """
    status = state["orchestration_state"].task_status.get(task_key)
    if status is None:
        logger.warning(
            f"Transition '{task_key}' -> '{next_node}': task_status key missing. "
            f"Node may not have run. Halting graph."
        )
        return END
    if status in _ADVANCE_STATUSES:
        logger.debug(f"Transition '{task_key}' [{status}] -> '{next_node}'")
        return next_node
    if status in _HALT_STATUSES:
        logger.info(f"Transition '{task_key}' [{status}] -> END (cancelled)")
        return END
    # RUNNING or any unknown status — the node didn't finish cleanly
    logger.error(
        f"Transition '{task_key}' [{status}] -> END. "
        f"Node left in non-terminal state. This is a bug — check logs for exceptions in the node."
    )
    return END


def planner_transition(state: GraphState) -> str:
    return _transition(state, "planner", "passive_recon_node")

def passive_recon_transition(state: GraphState) -> str:
    return _transition(state, "passive_recon", "scope_enforcement_node")

def scope_enforcement_transition(state: GraphState) -> str:
    return _transition(state, "scope_enforcement", "active_recon_node")

def active_recon_transition(state: GraphState) -> str:
    return _transition(state, "active_recon", "js_node")

def js_transition(state: GraphState) -> str:
    return _transition(state, "js", "api_node")

def api_transition(state: GraphState) -> str:
    return _transition(state, "api", "parameter_node")

def parameter_transition(state: GraphState) -> str:
    return _transition(state, "parameter", "vulnerability_node")

def vuln_transition(state: GraphState) -> str:
    return _transition(state, "vulnerability", "analysis_node")

def analysis_transition(state: GraphState) -> str:
    return _transition(state, "analysis", "report_node")
