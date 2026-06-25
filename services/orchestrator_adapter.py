import threading
from typing import Dict, Any, Optional, List
from orchestrator.graph import build_graph
from schemas.state import ExecutionState
from schemas.target import TargetState
from orchestrator.orchestration_state import OrchestrationState
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry, JobStatus
from storage.database import get_db_session
from storage.repositories.report_repository import ReportRepository
from schemas.report import Report

class OrchestratorAdapter:
    def __init__(self, job_registry: JobRegistry, config: BugHunterConfig):
        self._job_registry = job_registry
        self._config = config
        self._app = build_graph(config)
        self._threads: Dict[str, threading.Thread] = {}

    def run_scan(self, job_id: str, target: TargetState) -> None:
        """Run the scan synchronously, updating the job registry."""
        self._job_registry.update_status(job_id, JobStatus.RUNNING)
        self._job_registry.update_progress(job_id, "init", 0.0)
        
        initial_exec_state = ExecutionState(target=target)
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
        
        # Calculate progress
        stages = ["init_node", "recon_node", "js_node", "api_node", "vulnerability_node", "analysis_node", "report_node"]
        
        try:
            for i, output in enumerate(self._app.stream(graph_state_input, config=config_run)):
                # Check for cancellation
                job = self._job_registry.get_job(job_id)
                if job and job.status == JobStatus.CANCELLED:
                    return # Stop execution safely
                    
                if output:
                    node_name = list(output.keys())[0]
                    progress = min(100.0, ((i + 1) / len(stages)) * 100.0)
                    self._job_registry.update_progress(job_id, node_name, progress)
            
            self._job_registry.update_progress(job_id, "completed", 100.0)
            self._job_registry.update_status(job_id, JobStatus.COMPLETED)
            
        except Exception as e:
            self._job_registry.update_status(job_id, JobStatus.FAILED, str(e))

    def submit_scan(self, job_id: str, target: TargetState) -> None:
        """Submit a scan to run in the background."""
        thread = threading.Thread(target=self.run_scan, args=(job_id, target), daemon=True)
        self._threads[job_id] = thread
        thread.start()

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self._job_registry.get_job(job_id)
        if not job:
            return None
        return {
            "job_id": job.job_id,
            "target": job.target_domain,
            "status": job.status.value,
            "progress": job.progress,
            "current_stage": job.current_stage,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error": job.error
        }
        
    def get_report(self, job_id: str) -> List[Report]:
        """Fetch report definitions for a job from storage."""
        # Using session_id = job_id
        with get_db_session() as session:
            repo = ReportRepository()
            reports = repo.get_by_session(session, job_id)
            return reports

    def cancel(self, job_id: str) -> bool:
        job = self._job_registry.get_job(job_id)
        if job and job.status in (JobStatus.PENDING, JobStatus.RUNNING):
            self._job_registry.update_status(job_id, JobStatus.CANCELLED)
            return True
        return False
