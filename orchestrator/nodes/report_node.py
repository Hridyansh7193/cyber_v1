from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from agents.reporter_agent import generate_reports
from orchestrator.delta_applier import apply_report_delta
from orchestrator.queue_manager import start_task, complete_task

def report_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    if not any(t.name == "node:report_node" for t in state.execution_state.task_queue):
        new_orch = start_task(state.orchestration_state, "report")
        new_orch = complete_task(new_orch, "report")
        return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)

    orch = start_task(state.orchestration_state, "report")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        agent=generate_reports,
        delta_applier=apply_report_delta
    )
    orch = complete_task(orch, "report")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
