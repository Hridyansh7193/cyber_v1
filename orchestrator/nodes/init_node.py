from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.queue_manager import update_task_status

def init_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    new_orch = update_task_status(state.orchestration_state, "init", "COMPLETED")
    return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)
