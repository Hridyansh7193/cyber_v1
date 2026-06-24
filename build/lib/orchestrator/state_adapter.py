from orchestrator.graph_state import GraphState
from orchestrator.node_result import NodeResult

def to_graph_state(result: NodeResult) -> GraphState:
    return {
        "execution_state": result.execution_state,
        "orchestration_state": result.orchestration_state
    }

def from_graph_state(state: GraphState) -> NodeResult:
    return NodeResult(
        execution_state=state["execution_state"],
        orchestration_state=state["orchestration_state"]
    )
