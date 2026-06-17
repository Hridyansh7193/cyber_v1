from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from agents.analyzer import associate
from orchestrator.delta_applier import apply_analysis_delta

def analysis_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    return execute_node(
        state=state,
        config=config,
        task_name="analysis",
        wrapper=None,
        wrapper_applier=None,
        agent=associate,
        delta_applier=apply_analysis_delta
    )
