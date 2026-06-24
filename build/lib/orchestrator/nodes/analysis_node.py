from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from agents.analyzer import associate
from orchestrator.delta_applier import apply_analysis_delta
from orchestrator.queue_manager import start_task, complete_task

def analysis_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    orch = start_task(state.orchestration_state, "analysis")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        wrapper=None,
        wrapper_applier=None,
        agent=associate,
        delta_applier=apply_analysis_delta
    )
    orch = complete_task(orch, "analysis")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
