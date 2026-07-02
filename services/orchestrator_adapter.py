import threading
from typing import Dict, Any, Optional, List
from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from schemas.target import TargetState
from schemas.runtime_context import RuntimeContext
from orchestrator.orchestration_state import OrchestrationState
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry, JobStatus
from utils.logger import get_logger

logger = get_logger("orchestrator_adapter")

class OrchestratorAdapter:
    def __init__(self, job_registry: JobRegistry, config: BugHunterConfig):
        self._job_registry = job_registry
        self._config = config
        self._app = build_graph(config)

    def run_scan(self, job_id: str, target: TargetState, runtime_context: Optional[RuntimeContext] = None, resume_state: Optional[ExecutionState] = None) -> Optional[ExecutionState]:
        """Run the scan synchronously, returning the final ExecutionState."""
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
        graph_state_input = {
            "execution_state": initial_exec_state,
            "orchestration_state": initial_state
        }
        
        stages = ["init_node", "planner_node", "recon_node", "js_node", "api_node", "vulnerability_node", "analysis_node", "report_node"]
        final_state = initial_exec_state
        
        try:
            for i, output in enumerate(self._app.stream(graph_state_input, config=config_run)):
                job = self._job_registry.get_job(job_id)
                if job and job.status == JobStatus.CANCELLED:
                    return None
                    
                if output:
                    node_name = list(output.keys())[0]
                    node_result = output[node_name]
                    
                    if isinstance(node_result, dict) and "execution_state" in node_result:
                        final_state = node_result["execution_state"]
                    elif hasattr(node_result, "execution_state"):
                        final_state = node_result.execution_state
                        
                    progress = min(100.0, ((i + 1) / len(stages)) * 100.0)
                    self._job_registry.update_progress(job_id, node_name, progress)
                    logger.info(f"Node '{node_name}' completed (Progress: {progress:.1f}%)")
                    
                    # Create checkpoint after each node
                    try:
                        import os
                        import json
                        session_dir = os.path.join("workspaces", final_state.target.domain, "sessions", job_id)
                        if os.path.exists(session_dir):
                            checkpoint_path = os.path.join(session_dir, "checkpoint.json")
                            with open(checkpoint_path, "w", encoding="utf-8") as f:
                                f.write(final_state.model_dump_json(indent=2))
                    except Exception as e:
                        logger.warning(f"Failed to create checkpoint: {e}")
            
            self._job_registry.update_progress(job_id, "completed", 100.0)
            self._job_registry.update_status(job_id, JobStatus.COMPLETED)
            
            logger.info(f"Scan Pipeline completed for job {job_id}")
            logger.debug(f"Stats - Reports: {len(final_state.reports)}, Findings: {len(final_state.findings)}, "
                         f"Recon: {len(final_state.recon_state.subdomains)}, JS: {len(final_state.js_state.js_files)}, "
                         f"API: {len(final_state.api_state.swagger_urls)}, Vuln: {len(final_state.vuln_state.nuclei_results)}")
            return final_state
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Scan pipeline failed for job {job_id}", exc_info=True)
            self._job_registry.update_status(job_id, JobStatus.FAILED, str(e))
            return None

    def cancel(self, job_id: str) -> bool:
        job = self._job_registry.get_job(job_id)
        if job and job.status in (JobStatus.PENDING, JobStatus.RUNNING):
            self._job_registry.update_status(job_id, JobStatus.CANCELLED)
            return True
        return False
