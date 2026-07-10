import os
import threading
import datetime
from typing import Any, Optional
from orchestrator.graph import build_graph
from orchestrator.lifecycle_monitor import get_monitor, NodeTransition
from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.runtime_context import RuntimeContext
from orchestrator.orchestration_state import OrchestrationState
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry, JobStatus
from utils.logger import get_logger

logger = get_logger("orchestrator_adapter")
monitor = get_monitor()


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class OrchestratorAdapter:
    def __init__(self, job_registry: JobRegistry, config: BugHunterConfig, checkpointer: Optional[Any] = None):
        self._job_registry = job_registry
        self._config = config
        if checkpointer is None:
            from orchestrator.checkpoint_manager import CheckpointManager
            checkpointer_path = os.path.join(os.getcwd(), "workspaces", "checkpoints.db")
            checkpointer = CheckpointManager(db_path=checkpointer_path)
            
        self._checkpointer = checkpointer
        self._app = build_graph(config, checkpointer=self._checkpointer)

    def run_scan(self, job_id: str, target: TargetState, runtime_context: Optional[RuntimeContext] = None, resume_state: Optional[ExecutionState] = None) -> Optional[ExecutionState]:
        """Run the scan synchronously, returning the final ExecutionState."""
        tid = threading.get_ident()
        pid = os.getpid()
        
        logger.info(
            f"[LIFECYCLE] SCAN_START | job={job_id} | target={target.domain} "
            f"| pid={pid} | tid={tid} | ts={_now_iso()}"
        )
        
        self._job_registry.update_status(job_id, JobStatus.RUNNING)
        self._job_registry.update_progress(job_id, "init", 0.0)
        
        initial_exec_state = resume_state if resume_state else ExecutionState(target=target, runtime_context=runtime_context)
        initial_state = OrchestrationState(
            execution_state=initial_exec_state,
            config=self._config,
            task_status={},
            errors={}
        )
        
        config_run = {"configurable": {"thread_id": job_id}}
        
        # Check if we are resuming from the checkpointer natively
        graph_state_input = {
            "execution_state": initial_exec_state,
            "orchestration_state": initial_state
        }
        if self._checkpointer:
            try:
                saved_state = self._checkpointer.load(config_run)
                if saved_state and hasattr(saved_state, "values") and saved_state.values:
                    logger.info(f"[LIFECYCLE] CHECKPOINT_RESUME | job={job_id} | ts={_now_iso()}")
                    graph_state_input = None
                    
                    # Re-inject execution state if available
                    if "execution_state" in saved_state.values:
                        initial_exec_state = saved_state.values["execution_state"]
                else:
                    logger.info(f"[LIFECYCLE] CHECKPOINT_NONE | job={job_id} | Starting fresh.")
            except Exception as cp_err:
                logger.warning(
                    f"[LIFECYCLE] CHECKPOINT_LOAD_ERROR | job={job_id} | err={cp_err} | "
                    f"Starting fresh to avoid corrupt state."
                )
                # Keep graph_state_input as the fresh initial state — don't use None
                
        stages = [
            "init_node", "planner_node", "passive_recon_node", 
            "scope_enforcement_node", "active_recon_node", 
            "js_node", "api_node", "parameter_node", 
            "vulnerability_node", "analysis_node", "report_node"
        ]
        final_state = initial_exec_state
        node_transitions: dict[str, NodeTransition] = {}
        
        try:
            # Start watchdog to detect stalled nodes
            monitor.start_watchdog()
            monitor.scan_start(job_id, target.domain)
            
            # Stream graph execution with comprehensive tracking
            stream_iter = self._app.stream(graph_state_input, config=config_run)
            last_node_name = None
            
            for i, output in enumerate(stream_iter):
                job = self._job_registry.get_job(job_id)
                if job and job.status == JobStatus.CANCELLED:
                    logger.info(f"[LIFECYCLE] SCAN_CANCELLED | job={job_id} | ts={_now_iso()}")
                    # Mark current node as cancelled
                    if last_node_name and last_node_name in node_transitions:
                        monitor.node_exit(
                            node_transitions[last_node_name],
                            status="CANCELLED"
                        )
                    return None
                    
                if output:
                    node_name = list(output.keys())[0]
                    
                    # Log node entry on first appearance
                    if node_name not in node_transitions:
                        transition = monitor.node_enter(job_id, node_name)
                        node_transitions[node_name] = transition
                        last_node_name = node_name
                    
                    # Extract execution state from output
                    node_result = output[node_name]
                    if isinstance(node_result, dict) and "execution_state" in node_result:
                        final_state = node_result["execution_state"]
                    elif hasattr(node_result, "execution_state"):
                        final_state = node_result.execution_state
                    
                    # Calculate and update progress
                    if node_name in stages:
                        stage_idx = stages.index(node_name)
                        progress = min(100.0, ((stage_idx + 1) / len(stages)) * 100.0)
                    else:
                        progress = min(100.0, ((i + 1) / len(stages)) * 100.0)
                    
                    self._job_registry.update_progress(job_id, node_name, progress)
                    
                    logger.info(
                        f"[LIFECYCLE] NODE_STREAM_OUTPUT | job={job_id} | node={node_name} "
                        f"| progress={progress:.1f}% | ts={_now_iso()}"
                    )
                    
                    # Create checkpoint after each node
                    try:
                        session_dir = os.path.join("workspaces", final_state.target.domain, "sessions", job_id)
                        if os.path.exists(session_dir):
                            checkpoint_path = os.path.join(session_dir, "checkpoint.json")
                            with open(checkpoint_path, "w", encoding="utf-8") as f:
                                f.write(final_state.model_dump_json(indent=2))
                    except Exception as cp_err:
                        logger.warning(f"Failed to create checkpoint: {cp_err}")
            
            # Stream completed - mark last node as successful
            if last_node_name and last_node_name in node_transitions:
                monitor.node_exit(
                    node_transitions[last_node_name],
                    status="SUCCESS"
                )
            
            # Mark all tracked nodes as complete
            self._job_registry.update_progress(job_id, "completed", 100.0)
            self._job_registry.update_status(job_id, JobStatus.COMPLETED)
            
            monitor.scan_complete(
                job_id,
                "COMPLETED",
                findings_count=len(final_state.findings) if final_state else 0
            )
            
            logger.info(
                f"[LIFECYCLE] SCAN_COMPLETE | job={job_id} | pid={pid} | tid={tid} "
                f"| findings={len(final_state.findings) if final_state else 0} "
                f"| reports={len(final_state.reports) if final_state else 0} "
                f"| ts={_now_iso()}"
            )
            return final_state
            
        except StopIteration:
            # Normal end of stream iteration
            if last_node_name and last_node_name in node_transitions:
                monitor.node_exit(
                    node_transitions[last_node_name],
                    status="SUCCESS"
                )
            
            self._job_registry.update_progress(job_id, "completed", 100.0)
            self._job_registry.update_status(job_id, JobStatus.COMPLETED)
            monitor.scan_complete(job_id, "COMPLETED")
            
            logger.info(
                f"[LIFECYCLE] SCAN_COMPLETE (StopIteration) | job={job_id} | ts={_now_iso()}"
            )
            return final_state
            
        except RuntimeError as re:
            # Handle LangGraph executor shutdown or similar runtime errors
            if "cannot schedule new futures after shutdown" in str(re):
                logger.critical(
                    f"[LIFECYCLE] EXECUTOR_SHUTDOWN | job={job_id} | error={str(re)} | "
                    f"This may indicate the executor thread pool was prematurely closed. "
                    f"Check for resource cleanup issues.",
                    exc_info=True
                )
            
            # Mark current node as failed if applicable
            if last_node_name and last_node_name in node_transitions:
                monitor.node_exit(
                    node_transitions[last_node_name],
                    status="FAILED",
                    error=str(re)
                )
            
            error_msg = f"RuntimeError: {str(re)}"
            logger.error(
                f"[LIFECYCLE] SCAN_FAILED | job={job_id} | error={error_msg} "
                f"| pid={pid} | tid={tid} | ts={_now_iso()}",
                exc_info=True
            )
            
            # Dump diagnostic info
            try:
                diagnostics = monitor.dump_diagnostics(job_id)
                logger.error(f"[LIFECYCLE] DIAGNOSTICS:\n{diagnostics}")
            except Exception as diag_err:
                logger.error(f"Failed to generate diagnostics: {diag_err}")
            
            self._job_registry.update_status(job_id, JobStatus.FAILED, error_msg)
            monitor.scan_failed(job_id, error_msg)
            return None
            
        except Exception as e:
            # Mark current node as failed if applicable
            if last_node_name and last_node_name in node_transitions:
                monitor.node_exit(
                    node_transitions[last_node_name],
                    status="FAILED",
                    error=str(e)
                )
            
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(
                f"[LIFECYCLE] SCAN_FAILED | job={job_id} | error={error_msg} "
                f"| pid={pid} | tid={tid} | ts={_now_iso()}",
                exc_info=True
            )
            
            # Dump diagnostic info
            diagnostics = monitor.dump_diagnostics(job_id)
            logger.error(f"[LIFECYCLE] DIAGNOSTICS:\n{diagnostics}")
            
            self._job_registry.update_status(job_id, JobStatus.FAILED, error_msg)
            monitor.scan_failed(job_id, error_msg)
            return None
            
        except BaseException as be:
            # Catches KeyboardInterrupt, SystemExit, MemoryError, etc.
            if last_node_name and last_node_name in node_transitions:
                monitor.node_exit(
                    node_transitions[last_node_name],
                    status="ABORTED",
                    error=type(be).__name__
                )
            
            logger.critical(
                f"[LIFECYCLE] SCAN_ABORTED | job={job_id} | signal={type(be).__name__} "
                f"| pid={pid} | tid={tid} | ts={_now_iso()}"
            )
            try:
                self._job_registry.update_status(job_id, JobStatus.FAILED, f"Aborted: {type(be).__name__}")
            except Exception:
                pass  # Registry may be unavailable during interpreter shutdown
            raise  # Re-raise so the thread/process teardown proceeds normally
            
        finally:
            # Always stop the watchdog
            monitor.stop_watchdog()

    def cancel(self, job_id: str) -> bool:
        job = self._job_registry.get_job(job_id)
        if job and job.status in (JobStatus.PENDING, JobStatus.RUNNING):
            self._job_registry.update_status(job_id, JobStatus.CANCELLED)
            logger.info(f"[LIFECYCLE] SCAN_CANCEL_REQUESTED | job={job_id} | ts={_now_iso()}")
            return True
        return False
