import time
import datetime
from urllib.parse import urlparse
from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from services.scope_manager import ScopeManager
from orchestrator.queue_manager import start_task, complete_task
from utils.logger import get_logger

logger = get_logger("scope_enforcement_node")

# Safety cap: if passive recon found more than this many URLs, process only the first N.
# Prevents O(N*M) regex loops from stalling the pipeline for minutes.
_MAX_URLS_TO_FILTER = 5_000

def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def scope_enforcement_node(state: NodeResult, config: BugHunterConfig) -> NodeResult:
    """Filters discovered assets against scope rules."""
    t_start = time.monotonic()
    job_id = (
        state.execution_state.runtime_context.trace.job_id
        if state.execution_state.runtime_context and state.execution_state.runtime_context.trace
        else "unknown"
    )
    logger.info(
        f"[LIFECYCLE] NODE_ENTER | node=scope_enforcement_node | job={job_id} | ts={_now_iso()}"
    )

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

    # 3. Filter URLs — cap at _MAX_URLS_TO_FILTER to prevent long blocking loops
    original_urls = list(recon.urls)
    url_count = len(original_urls)
    if url_count > _MAX_URLS_TO_FILTER:
        logger.warning(
            f"scope_enforcement_node: {url_count} URLs discovered — capping at "
            f"{_MAX_URLS_TO_FILTER} to prevent stall. Increase _MAX_URLS_TO_FILTER if needed."
        )
        original_urls = original_urls[:_MAX_URLS_TO_FILTER]

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
    if url_count > _MAX_URLS_TO_FILTER:
        logger.info(f"ScopeManager processed {_MAX_URLS_TO_FILTER}/{url_count} URLs (capped).")
    elif len(filtered_urls) < len(original_urls):
        logger.info(f"ScopeManager dropped {len(original_urls) - len(filtered_urls)} URLs.")

    # Apply changes
    new_recon = recon.model_copy(update={
        "subdomains": tuple(filtered_subs),
        "alive_hosts": tuple(filtered_hosts),
        "urls": tuple(filtered_urls)
    })

    new_exec = state.execution_state.model_copy(update={"recon_state": new_recon})
    orch = complete_task(orch, "scope_enforcement")

    elapsed = time.monotonic() - t_start
    logger.info(
        f"[LIFECYCLE] NODE_EXIT | node=scope_enforcement_node | job={job_id} "
        f"| elapsed={elapsed:.3f}s | subs={len(filtered_subs)} | hosts={len(filtered_hosts)} "
        f"| urls={len(filtered_urls)} | ts={_now_iso()}"
    )

    return NodeResult(execution_state=new_exec, orchestration_state=orch)
