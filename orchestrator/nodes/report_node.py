from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from agents.reporter import generate_reports
from orchestrator.delta_applier import apply_report_delta

def report_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    return execute_node(
        state=state,
        config=config,
        task_name="report",
        wrapper=None,
        wrapper_applier=None,
        agent=generate_reports,
        delta_applier=apply_report_delta
    )
