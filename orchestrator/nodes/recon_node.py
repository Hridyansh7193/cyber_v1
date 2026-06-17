from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from orchestrator.node_executor import execute_node
from orchestrator.wrapper_result_applier import apply_recon_wrapper_result
from agents.recon import analyze_recon
from orchestrator.delta_applier import apply_recon_delta

def dummy_recon_wrapper(state):
    # Dummy until Phase 4 integration
    return {"new_subdomains": [], "new_hosts": [], "new_urls": []}

def recon_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    return execute_node(
        state=state,
        config=config,
        task_name="recon",
        wrapper=dummy_recon_wrapper,
        wrapper_applier=apply_recon_wrapper_result,
        agent=analyze_recon,
        delta_applier=apply_recon_delta
    )
