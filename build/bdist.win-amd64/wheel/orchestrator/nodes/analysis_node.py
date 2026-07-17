from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from agents.analyzer_agent import analyze_intelligence
from orchestrator.delta_applier import apply_finding_delta
from orchestrator.queue_manager import start_task, complete_task

def analysis_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    if not any(t.name == "node:analysis_node" for t in state.execution_state.task_queue):
        new_orch = start_task(state.orchestration_state, "analysis")
        new_orch = complete_task(new_orch, "analysis")
        return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)

    orch = start_task(state.orchestration_state, "analysis")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        agent=analyze_intelligence,
        delta_applier=apply_finding_delta
    )
    orch = complete_task(orch, "analysis")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
