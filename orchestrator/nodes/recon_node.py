from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_recon_wrapper_result
from agents.recon import analyze_recon
from orchestrator.delta_applier import apply_recon_delta
from orchestrator.queue_manager import start_task, complete_task
from schemas.tool_result import ToolResult

def dummy_recon_wrapper(state) -> ToolResult:
    return ToolResult(tool_name="dummy", metadata={"new_subdomains": [], "new_hosts": [], "new_urls": []}, errors=[], success=True, exit_code=0, stdout="", stderr="", execution_time=0.0)

def recon_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    orch = start_task(state.orchestration_state, "recon")
    new_exec = execute_node(
        current_exec=state.execution_state,
        config=config,
        wrapper=dummy_recon_wrapper,
        wrapper_applier=apply_recon_wrapper_result,
        agent=analyze_recon,
        delta_applier=apply_recon_delta
    )
    orch = complete_task(orch, "recon")
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
