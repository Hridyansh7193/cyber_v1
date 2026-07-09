from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from services.scope_manager import ScopeManager
from orchestrator.queue_manager import start_task, complete_task
from utils.logger import get_logger

logger = get_logger("scope_enforcement_node")

def scope_enforcement_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    """Filters discovered assets against scope rules."""
    
    # 1. Setup scope manager
    target = state.execution_state.target
    in_scope = list(target.scope) if target.scope else [target.domain, f"*.{target.domain}"]
    out_of_scope = list(target.out_of_scope) if target.out_of_scope else []
    
    scope_manager = ScopeManager(in_scope=in_scope, out_of_scope=out_of_scope)
    
    # 2. Filter subdomains
    orch = start_task(state.orchestration_state, "scope_enforcement")
    
    recon = state.execution_state.recon_state
    original_subs = list(recon.subdomains)
    filtered_subs = scope_manager.filter_targets(original_subs)
    
    original_hosts = list(recon.alive_hosts)
    filtered_hosts = scope_manager.filter_targets(original_hosts)
    
    original_urls = list(recon.urls)
    # URLs must be parsed to just the domain for scope filtering, or we filter the full URL
    # ScopeManager can filter full URLs if regex is used, but for CIDR/domain matches we need the netloc.
    from urllib.parse import urlparse
    filtered_urls = []
    for u in original_urls:
        if "://" in u:
            netloc = urlparse(u).netloc.split(":")[0]
            if scope_manager.is_in_scope(netloc):
                filtered_urls.append(u)
        else:
            if scope_manager.is_in_scope(u):
                filtered_urls.append(u)
                
    if len(filtered_subs) < len(original_subs):
        logger.info(f"ScopeManager dropped {len(original_subs) - len(filtered_subs)} subdomains.")
    if len(filtered_hosts) < len(original_hosts):
        logger.info(f"ScopeManager dropped {len(original_hosts) - len(filtered_hosts)} alive hosts.")
        
    # Apply changes
    new_recon = recon.model_copy(update={
        "subdomains": tuple(filtered_subs),
        "alive_hosts": tuple(filtered_hosts),
        "urls": tuple(filtered_urls)
    })
    
    new_exec = state.execution_state.model_copy(update={"recon_state": new_recon})
    orch = complete_task(orch, "scope_enforcement")
    
    return NodeResult(execution_state=new_exec, orchestration_state=orch)
