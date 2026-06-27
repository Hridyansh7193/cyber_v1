from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from agents.reporter import generate_reports
from orchestrator.delta_applier import apply_report_delta
from orchestrator.queue_manager import start_task, complete_task

def report_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    orch = start_task(state.orchestration_state, "report")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        agent=generate_reports,
        delta_applier=apply_report_delta
    )
    orch = complete_task(orch, "report")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
