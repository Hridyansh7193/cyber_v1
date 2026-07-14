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
_MAX_URLS_TO_FILTER = 2_000

# Timeout for URL filtering (seconds). If taking longer, abort and use partial results.
_URL_FILTER_TIMEOUT_SEC = 60.0  # 1 minute

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
        logger.info(f"ScopeManager initialized: in_scope={len(in_scope)}, out_of_scope={len(out_of_scope)}")

        # 2. Filter subdomains
        orch = start_task(state.orchestration_state, "scope_enforcement")

        recon = state.execution_state.recon_state
        original_subs = list(recon.subdomains)
        logger.info(f"[SCOPE] Filtering {len(original_subs)} subdomains...")
        
        t_filter_subs = time.monotonic()
        filtered_subs = scope_manager.filter_targets(original_subs)
        elapsed_subs = time.monotonic() - t_filter_subs
        logger.info(f"[SCOPE] Subdomains: {len(original_subs)} → {len(filtered_subs)} ({elapsed_subs:.3f}s)")

        original_hosts = list(recon.alive_hosts)
        logger.info(f"[SCOPE] Filtering {len(original_hosts)} hosts...")
        
        t_filter_hosts = time.monotonic()
        filtered_hosts = scope_manager.filter_targets(original_hosts)
        elapsed_hosts = time.monotonic() - t_filter_hosts
        logger.info(f"[SCOPE] Hosts: {len(original_hosts)} → {len(filtered_hosts)} ({elapsed_hosts:.3f}s)")

        # 3. Filter URLs — cap at _MAX_URLS_TO_FILTER to prevent long blocking loops
        original_urls = list(recon.urls)
        url_count = len(original_urls)
        
        logger.info(f"[SCOPE] Starting URL filtering: {url_count} total URLs...")
        
        if url_count > _MAX_URLS_TO_FILTER:
            logger.warning(
                f"[SCOPE] URL cap: {url_count} URLs discovered > {_MAX_URLS_TO_FILTER} limit. "
                f"Processing only first {_MAX_URLS_TO_FILTER}."
            )
            original_urls = original_urls[:_MAX_URLS_TO_FILTER]

        logger.info(f"[SCOPE] Beginning URL filtering loop ({len(original_urls)} URLs)...")
        t_filter_urls = time.monotonic()
        
        filtered_urls = []
        log_interval = min(100, max(len(original_urls) // 10, 1))  # Log 10 times during filtering
        timeout_at = t_filter_urls + _URL_FILTER_TIMEOUT_SEC
        
        for i, u in enumerate(original_urls):
            if i >= _MAX_URLS_TO_FILTER:
                break
            # Check for timeout
            if time.monotonic() > timeout_at:
                logger.error(
                    f"[SCOPE] URL filtering TIMEOUT after {_URL_FILTER_TIMEOUT_SEC}s! "
                    f"Processed {i}/{len(original_urls)} URLs. "
                    f"Aborting filtering to prevent indefinite stall."
                )
                # Keep what we've filtered so far
                break
            
            # Log progress every log_interval
            if i % log_interval == 0 and i > 0:
                elapsed_so_far = time.monotonic() - t_filter_urls
                rate = i / elapsed_so_far if elapsed_so_far > 0 else 0
                remaining = len(original_urls) - i
                eta_sec = remaining / rate if rate > 0 else 0
                logger.info(
                    f"[SCOPE] URL progress: {i}/{len(original_urls)} "
                    f"({100*i/len(original_urls):.1f}%) | "
                    f"rate={rate:.0f} URLs/s | ETA={eta_sec:.0f}s"
                )
            
            normalized = str(u).strip()
            if not normalized:
                continue

            if "://" in normalized:
                try:
                    parsed = urlparse(normalized)
                    host = parsed.netloc.split(":")[0].lower()
                    if scope_manager.is_in_scope(host):
                        filtered_urls.append(normalized)
                except Exception as parse_err:
                    logger.warning(f"[SCOPE] Failed to parse URL '{normalized[:50]}...': {parse_err}")
            else:
                if scope_manager.is_in_scope(normalized):
                    filtered_urls.append(normalized)
        
        elapsed_urls = time.monotonic() - t_filter_urls
        rate = len(original_urls) / elapsed_urls if elapsed_urls > 0 else 0
        logger.info(
            f"[SCOPE] URL filtering complete: {len(original_urls)} → {len(filtered_urls)} "
            f"({elapsed_urls:.3f}s, {rate:.0f} URLs/s)"
        )

        if len(filtered_subs) < len(original_subs):
            logger.info(f"[SCOPE] Dropped {len(original_subs) - len(filtered_subs)} subdomains (out of scope)")
        if len(filtered_hosts) < len(original_hosts):
            logger.info(f"[SCOPE] Dropped {len(original_hosts) - len(filtered_hosts)} hosts (out of scope)")
        if url_count > _MAX_URLS_TO_FILTER:
            logger.info(f"[SCOPE] Dropped {url_count - len(original_urls)} URLs (capped)")
        elif len(filtered_urls) < len(original_urls):
            logger.info(f"[SCOPE] Dropped {len(original_urls) - len(filtered_urls)} URLs (out of scope)")

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
