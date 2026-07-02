from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_recon_wrapper_result
from agents.recon import analyze_recon
from orchestrator.delta_applier import apply_recon_delta
from orchestrator.queue_manager import start_task, complete_task
from execution.wrappers import ReconWrapper
from schemas.runtime import Capability

def active_recon_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    if state.execution_state.intelligence and state.execution_state.intelligence.planner:
        if "active_recon_node" in state.execution_state.intelligence.planner.skipped_nodes:
            new_orch = start_task(state.orchestration_state, "active_recon")
            new_orch = complete_task(new_orch, "active_recon")
            return NodeResult(execution_state=state.execution_state, orchestration_state=new_orch)

    orch = start_task(state.orchestration_state, "active_recon")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        capability=Capability.RECON,
        wrapper_func=ReconWrapper.execute,
        wrapper_applier=apply_recon_wrapper_result,
        agent=analyze_recon,
        delta_applier=apply_recon_delta
    )
    orch = complete_task(orch, "active_recon")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
