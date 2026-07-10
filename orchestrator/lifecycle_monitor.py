"""
Comprehensive lifecycle monitoring for orchestration graph execution.

Tracks node entry/exit, progress updates, exceptions, and thread state
to diagnose issues like silent worker death or orchestration stalls.
"""

import time
import threading
import traceback
import datetime
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from utils.logger import get_logger

logger = get_logger("lifecycle_monitor")


@dataclass
class NodeTransition:
    """Tracks a single node execution."""
    node_name: str
    job_id: str
    entry_time: float = field(default_factory=time.monotonic)
    exit_time: Optional[float] = None
    thread_id: int = field(default_factory=threading.get_ident)
    process_id: int = field(default_factory=__import__('os').getpid)
    status: str = "RUNNING"  # RUNNING, SUCCESS, FAILED, TIMEOUT
    error: Optional[str] = None
    elapsed_seconds: Optional[float] = None
    
    def mark_complete(self, status="SUCCESS", error=None):
        """Mark node as complete and calculate elapsed time."""
        self.exit_time = time.monotonic()
        self.status = status
        self.error = error
        self.elapsed_seconds = self.exit_time - self.entry_time
        
    def to_dict(self):
        """Convert to dict for logging."""
        return {
            "node": self.node_name,
            "job": self.job_id,
            "status": self.status,
            "elapsed_s": self.elapsed_seconds,
            "thread_id": self.thread_id,
            "error": self.error
        }


class LifecycleMonitor:
    """
    Monitors orchestration lifecycle events.
    
    Logs node transitions and detects:
    - Silent node failures
    - Stalled nodes (taking too long)
    - Worker thread death
    - Unhandled exceptions
    """
    
    def __init__(self, warn_node_timeout_sec: float = 300.0):
        """
        Args:
            warn_node_timeout_sec: Warn if a node takes longer than this.
        """
        self.warn_node_timeout_sec = warn_node_timeout_sec
        self._transitions: Dict[str, list[NodeTransition]] = defaultdict(list)
        self._lock = threading.Lock()
        self._watchdog_thread: Optional[threading.Thread] = None
        self._watchdog_running = False
        self._poll_interval = 5.0
        
    def start_watchdog(self):
        """Start background watchdog thread to detect stalled nodes."""
        if self._watchdog_running:
            return
            
        self._watchdog_running = True
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            daemon=False,
            name="lifecycle-watchdog"
        )
        self._watchdog_thread.start()
        logger.debug("[LIFECYCLE] Watchdog started")
        
    def stop_watchdog(self):
        """Stop background watchdog thread."""
        self._watchdog_running = False
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=5.0)
        logger.debug("[LIFECYCLE] Watchdog stopped")
        
    def _watchdog_loop(self):
        """Periodically check for stalled nodes."""
        while self._watchdog_running:
            try:
                current_time = time.monotonic()
                
                with self._lock:
                    for job_id, transitions in self._transitions.items():
                        if not transitions:
                            continue
                            
                        last = transitions[-1]
                        if last.status == "RUNNING":
                            elapsed = current_time - last.entry_time
                            if elapsed > self.warn_node_timeout_sec:
                                logger.warning(
                                    f"[LIFECYCLE] NODE_STALLED | node={last.node_name} | "
                                    f"job={job_id} | elapsed={elapsed:.1f}s "
                                    f"(threshold={self.warn_node_timeout_sec}s)"
                                )
                                
                time.sleep(self._poll_interval)
            except Exception as e:
                logger.error(f"[LIFECYCLE] Watchdog error: {e}", exc_info=True)
                
    def node_enter(self, job_id: str, node_name: str) -> NodeTransition:
        """Record node entry."""
        transition = NodeTransition(node_name=node_name, job_id=job_id)
        
        with self._lock:
            self._transitions[job_id].append(transition)
            
        logger.info(
            f"[LIFECYCLE] NODE_ENTER | job={job_id} | node={node_name} | "
            f"pid={transition.process_id} | tid={transition.thread_id} | "
            f"ts={_now_iso()}"
        )
        return transition
        
    def node_exit(
        self, 
        transition: NodeTransition, 
        status: str = "SUCCESS",
        error: Optional[str] = None
    ):
        """Record node exit."""
        transition.mark_complete(status=status, error=error)
        
        logger.info(
            f"[LIFECYCLE] NODE_EXIT | job={transition.job_id} | node={transition.node_name} | "
            f"status={status} | elapsed={transition.elapsed_seconds:.3f}s | "
            f"ts={_now_iso()}" + (f" | error={error}" if error else "")
        )
        
        if status == "FAILED" and error:
            logger.error(
                f"[LIFECYCLE] NODE_FAILED | job={transition.job_id} | "
                f"node={transition.node_name} | error={error}"
            )
            
    def scan_start(self, job_id: str, target: str):
        """Record scan start."""
        logger.info(
            f"[LIFECYCLE] SCAN_START | job={job_id} | target={target} | "
            f"pid={__import__('os').getpid()} | ts={_now_iso()}"
        )
        
    def scan_complete(self, job_id: str, status: str, findings_count: int = 0):
        """Record scan completion."""
        with self._lock:
            transitions = self._transitions.get(job_id, [])
            
        logger.info(
            f"[LIFECYCLE] SCAN_COMPLETE | job={job_id} | status={status} | "
            f"nodes={len(transitions)} | findings={findings_count} | ts={_now_iso()}"
        )
        
    def scan_failed(self, job_id: str, error: str):
        """Record scan failure."""
        logger.error(
            f"[LIFECYCLE] SCAN_FAILED | job={job_id} | error={error} | ts={_now_iso()}"
        )
        
    def thread_check(self, job_id: str, worker_thread: Optional[threading.Thread]):
        """Log worker thread status."""
        if worker_thread is None:
            logger.warning(
                f"[LIFECYCLE] THREAD_CHECK | job={job_id} | status=NOT_FOUND"
            )
            return False
            
        is_alive = worker_thread.is_alive()
        logger.debug(
            f"[LIFECYCLE] THREAD_CHECK | job={job_id} | alive={is_alive} | "
            f"name={worker_thread.name}"
        )
        return is_alive
        
    def get_transitions(self, job_id: str) -> list[NodeTransition]:
        """Get all transitions for a job."""
        with self._lock:
            return list(self._transitions.get(job_id, []))
            
    def dump_diagnostics(self, job_id: str) -> str:
        """Generate diagnostic report for a job."""
        transitions = self.get_transitions(job_id)
        lines = [
            f"Job {job_id} - Lifecycle Diagnostics",
            f"Total nodes executed: {len(transitions)}",
            ""
        ]
        
        current_time = time.monotonic()
        
        for t in transitions:
            status_mark = "✓" if t.status == "SUCCESS" else "✗" if t.status == "FAILED" else "⏳"
            
            # Calculate elapsed time - use stored value if available, otherwise compute from entry time
            if t.elapsed_seconds is not None:
                elapsed = t.elapsed_seconds
            else:
                # Node may still be running or failed before mark_complete was called
                exit_time = t.exit_time if t.exit_time is not None else current_time
                elapsed = exit_time - t.entry_time
            
            lines.append(
                f"{status_mark} {t.node_name}: {elapsed:.2f}s "
                f"({t.status})" + (f" - {t.error}" if t.error else "")
            )
            
        total_time = sum(
            (t.elapsed_seconds if t.elapsed_seconds is not None else 
             (t.exit_time - t.entry_time if t.exit_time else current_time - t.entry_time))
            for t in transitions
        )
        lines.append(f"Total: {total_time:.2f}s")
        
        return "\n".join(lines)


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# Global singleton monitor
_monitor: Optional[LifecycleMonitor] = None

def get_monitor() -> LifecycleMonitor:
    """Get or create the global lifecycle monitor."""
    global _monitor
    if _monitor is None:
        _monitor = LifecycleMonitor()
    return _monitor
