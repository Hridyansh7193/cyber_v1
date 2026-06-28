import threading
from typing import Dict, Any, Optional
from services.orchestrator_adapter import OrchestratorAdapter
from services.job_registry import JobRegistry, JobStatus
from services.target_service import TargetService
from services.persistence_service import PersistenceService
from services.report_service import ReportService
from services.workspace_service import WorkspaceService
from config.schemas import BugHunterConfig
from utils.logger import get_logger

logger = get_logger("scan_service")

class ScanService:
    """Orchestrates scan execution, persistence, and workspace output."""
    
    def __init__(self, 
                 adapter: OrchestratorAdapter, 
                 registry: JobRegistry,
                 persistence_service: PersistenceService = None,
                 report_service: ReportService = None,
                 workspace_service: WorkspaceService = None):
        self._adapter = adapter
        self._registry = registry
        self._persistence_service = persistence_service
        self._report_service = report_service
        self._workspace_service = workspace_service
        self._threads: Dict[str, threading.Thread] = {}

    def submit_scan(self, domain: str, config: BugHunterConfig, metadata: dict = None) -> str:
        job_id = self._registry.create_job(domain, metadata)
        thread = threading.Thread(target=self.run_scan_sync, args=(domain, config, metadata, job_id), daemon=True)
        self._threads[job_id] = thread
        thread.start()
        return job_id
        
    def run_scan_sync(self, domain: str, config: BugHunterConfig, metadata: dict = None, job_id: str = None) -> str:
        if not job_id:
            job_id = self._registry.create_job(domain, metadata)
            
        target = TargetService.normalize_target(domain, job_id, metadata)
        logger.info(f"Scan started for target: {domain} (Job: {job_id})")
        
        final_state = self._adapter.run_scan(job_id, target)
        
        if final_state:
            logger.info("Scan finished successfully.")
            logger.debug(f"Final state: {final_state}")
            
            # 1. Persist to DB
            if self._persistence_service:
                self._persistence_service.save_findings(job_id, final_state.findings)
                self._persistence_service.save_reports(final_state.reports)
                if hasattr(final_state, 'logs') and final_state.logs:
                    self._persistence_service.save_telemetry(final_state.logs)
                logger.debug("Database persistence complete.")
                
            # 2. Render Reports
            rendered_reports = []
            if self._report_service:
                rendered_reports = self._report_service.render_reports(final_state.reports)
                logger.info(f"Report rendered: {len(rendered_reports)} formats.")
                
            # 3. Write to Workspace
            if self._workspace_service and rendered_reports:
                self._workspace_service.save_reports(domain, job_id, rendered_reports)
                logger.debug("Workspace output written.")
                
        return job_id

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self._registry.get_job(job_id)
        if job:
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
            
        # Fallback to persistence service
        if self._persistence_service:
            session = self._persistence_service.get_session(job_id)
            if session:
                return {
                    "job_id": session.session_id,
                    "target": session.target_domain,
                    "status": session.status,
                    "progress": 100.0 if session.status in ["completed", "failed", "cancelled"] else 0.0,
                    "current_stage": "unknown",
                    "started_at": session.started_at,
                    "completed_at": session.finished_at,
                    "error": None
                }
        return None

    def cancel_scan(self, job_id: str) -> bool:
        return self._adapter.cancel(job_id)

    def get_report(self, job_id: str, format: str = "json"):
        from schemas.generated_report import GeneratedReport
        from schemas.report import ReportFormat
        
        if not self._persistence_service:
            return None
            
        reports = self._persistence_service.get_reports_for_session(job_id)
        for r in reports:
            if r.report_format.lower() == format.lower():
                try:
                    with open(r.report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return GeneratedReport(
                        report_id=r.id,
                        format=format.lower(),
                        filename=r.report_path.split("/")[-1] if "/" in r.report_path else r.report_path.split("\\")[-1],
                        mime_type="application/json" if format.lower() == "json" else "text/markdown",
                        content=content
                    )
                except Exception:
                    return None
        return None
