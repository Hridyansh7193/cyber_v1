import time
import datetime
from urllib.parse import urlparse
from config.schemas import BugHunterConfig
from orchestrator.node_result import NodeResult
from services.scope_manager import ScopeManager
from orchestrator.queue_manager import start_task, complete_task
from orchestrator.lifecycle_monitor import get_monitor
from utils.logger import get_logger

logger = get_logger("scope_enforcement_node")
monitor = get_monitor()

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
    
    # Use lifecycle monitor for entry
    transition = monitor.node_enter(job_id, "scope_enforcement_node")
    
    logger.info(
        f"[LIFECYCLE] NODE_ENTER | node=scope_enforcement_node | job={job_id} | ts={_now_iso()}"
    )

    try:
        # 1. Setup scope manager
        target = state.execution_state.target
        in_scope = list(target.scope) if target.scope else [target.domain, f"*.{target.domain}"]
        out_of_scope = list(target.out_of_scope) if target.out_of_scope else []

        scope_manager = ScopeManager(in_scope=in_scope, out_of_scope=out_of_scope)
        logger.debug(f"ScopeManager initialized: in_scope={len(in_scope)}, out_of_scope={len(out_of_scope)}")

        # 2. Filter subdomains
        orch = start_task(state.orchestration_state, "scope_enforcement")

        recon = state.execution_state.recon_state
        original_subs = list(recon.subdomains)
        logger.debug(f"Filtering {len(original_subs)} subdomains...")
        
        t_filter_subs = time.monotonic()
        filtered_subs = scope_manager.filter_targets(original_subs)
        elapsed_subs = time.monotonic() - t_filter_subs
        logger.debug(f"Subdomain filtering took {elapsed_subs:.3f}s")

        original_hosts = list(recon.alive_hosts)
        logger.debug(f"Filtering {len(original_hosts)} hosts...")
        
        t_filter_hosts = time.monotonic()
        filtered_hosts = scope_manager.filter_targets(original_hosts)
        elapsed_hosts = time.monotonic() - t_filter_hosts
        logger.debug(f"Host filtering took {elapsed_hosts:.3f}s")

        # 3. Filter URLs — cap at _MAX_URLS_TO_FILTER to prevent long blocking loops
        original_urls = list(recon.urls)
        url_count = len(original_urls)
        if url_count > _MAX_URLS_TO_FILTER:
            logger.warning(
                f"scope_enforcement_node: {url_count} URLs discovered — capping at "
                f"{_MAX_URLS_TO_FILTER} to prevent stall. Increase _MAX_URLS_TO_FILTER if needed."
            )
            original_urls = original_urls[:_MAX_URLS_TO_FILTER]

        logger.debug(f"Filtering {len(original_urls)} URLs...")
        t_filter_urls = time.monotonic()
        
        filtered_urls = []
        for i, u in enumerate(original_urls):
            if i % 100 == 0 and i > 0:
                logger.debug(f"  Progress: {i}/{len(original_urls)} URLs processed...")
            
            if "://" in u:
                try:
                    netloc = urlparse(u).netloc.split(":")[0]
                    if scope_manager.is_in_scope(netloc):
                        filtered_urls.append(u)
                except Exception as parse_err:
                    logger.warning(f"Failed to parse URL '{u}': {parse_err}")
            else:
                if scope_manager.is_in_scope(u):
                    filtered_urls.append(u)
        
        elapsed_urls = time.monotonic() - t_filter_urls
        logger.debug(f"URL filtering took {elapsed_urls:.3f}s")

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
        
        # Mark as successful
        monitor.node_exit(transition, status="SUCCESS")
        
        return NodeResult(execution_state=new_exec, orchestration_state=orch)
        
    except Exception as e:
        elapsed = time.monotonic() - t_start
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(
            f"[LIFECYCLE] NODE_FAILED | node=scope_enforcement_node | job={job_id} "
            f"| elapsed={elapsed:.3f}s | error={error_msg}",
            exc_info=True
        )
        monitor.node_exit(transition, status="FAILED", error=error_msg)
        raise
