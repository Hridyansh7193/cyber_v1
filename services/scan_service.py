import os
import threading
import datetime
from typing import Dict, Any, Optional
from services.orchestrator_adapter import OrchestratorAdapter
from services.job_registry import JobRegistry, JobStatus
from services.target_service import TargetService
from services.persistence_service import PersistenceService
from services.report_service import ReportService
from services.workspace_service import WorkspaceService
from config.schemas import BugHunterConfig
from utils.logger import get_logger
from schemas.runtime_context import RuntimeContext
from services.tool_manager import ToolManager
from services.wordlist_manager import WordlistManager
from services.target_resolver import TargetResolver

logger = get_logger("scan_service")


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

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

    def submit_scan(self, domain: str, config: BugHunterConfig, metadata: dict = None, resume_session_id: str = None) -> str:
        job_id = resume_session_id if resume_session_id else self._registry.create_job(domain, metadata)
        # Non-daemon thread: the worker must run to completion even after the CLI
        # main thread finishes. The CLI progress loop calls join() to wait for it.
        # daemon=True was the original bug that caused silent worker death.
        thread = threading.Thread(
            target=self.run_scan_sync,
            args=(domain, config, metadata, job_id, resume_session_id is not None),
            daemon=False,
            name=f"scan-worker-{job_id[:8]}"
        )
        self._threads[job_id] = thread
        logger.info(
            f"[LIFECYCLE] THREAD_START | job={job_id} | thread={thread.name} "
            f"| pid={os.getpid()} | ts={_now_iso()}"
        )
        thread.start()
        return job_id

    def get_worker_thread(self, job_id: str) -> Optional[threading.Thread]:
        """Return the worker thread for this job, or None if not found."""
        return self._threads.get(job_id)
        
    def run_scan_sync(self, domain: str, config: BugHunterConfig, metadata: dict = None, job_id: str = None, is_resume: bool = False) -> str:
        if not job_id:
            job_id = self._registry.create_job(domain, metadata)
            
        try:
            target = TargetService.normalize_target(domain, job_id, metadata)
        except ValueError as exc:
            error_msg = f"Invalid scan target: {exc}"
            logger.error(error_msg)
            self._registry.update_status(job_id, JobStatus.FAILED, error=error_msg)
            return job_id
        logger.info(f"Scan started for target: {domain} (Job: {job_id}){' (Resuming)' if is_resume else ''}")
        
        # Initialize Runtime Context
        tool_manager = ToolManager()
        tool_manager.detect()
        
        wordlist_manager = WordlistManager()
        wordlist_manager.detect()
        
        target_resolver = TargetResolver()
        target = target_resolver.resolve_target(target)
        
        runtime_context = RuntimeContext(
            tool_manager=tool_manager,
            wordlist_manager=wordlist_manager,
            target_resolver=target_resolver
        )
        runtime_context.trace.job_id = job_id
        runtime_context.trace.target = domain
        
        # PRE-FLIGHT CHECK: Environment Validation (Doctor)
        from runtime.doctor import Doctor
        doc = Doctor()
        report = doc.diagnose()
        
        if report.summary_fail > 0:
            error_msg = f"Environment validation failed. Found {report.summary_fail} missing dependencies/tools. Run `bughunter doctor` to see details."
            logger.error(error_msg)
            self._registry.update_status(job_id, JobStatus.FAILED, error=error_msg)
            return job_id
        
        if self._persistence_service and not is_resume:
            self._persistence_service.create_session(job_id, domain)
            
        if self._workspace_service and not is_resume:
            self._workspace_service.workspace_manager.create_session(job_id, domain, "default")
            
        # If resuming, load state from checkpoint
        resume_state = None
        if is_resume:
            try:
                import os
                import json
                from schemas.state import ExecutionState
                session_dir = os.path.join("workspaces", domain, "sessions", job_id)
                checkpoint_path = os.path.join(session_dir, "checkpoint.json")
                if os.path.exists(checkpoint_path):
                    with open(checkpoint_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        resume_state = ExecutionState(**data)
                        # Re-inject runtime_context since it doesn't serialize
                        resume_state = resume_state.model_copy(update={"runtime_context": runtime_context})
                        logger.info("Successfully loaded checkpoint for resumption.")
                else:
                    logger.warning(f"No checkpoint found at {checkpoint_path}. Starting fresh.")
            except Exception as e:
                logger.error(f"Failed to load checkpoint: {e}. Starting fresh.")
        
        final_state = self._adapter.run_scan(job_id, target, runtime_context, resume_state)
        
        if final_state:
            logger.info("Scan finished successfully.")
            logger.debug(f"Final state: {final_state}")
            
            # 1. Persist to DB
            if self._persistence_service:
                self._persistence_service.update_session(job_id, "completed")
                self._persistence_service.save_findings(job_id, final_state.findings)
                self._persistence_service.save_reports(final_state.reports)
                if hasattr(final_state, 'logs') and final_state.logs:
                    self._persistence_service.save_telemetry(job_id, final_state.logs)
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
                
            # 4. Save trace report
            if final_state.runtime_context and hasattr(final_state.runtime_context, "trace"):
                import datetime
                final_state.runtime_context.trace.finished_at = datetime.datetime.now(datetime.timezone.utc)
                trace_path = __import__('os').path.join("workspaces", domain, "sessions", job_id, "trace.json")
                try:
                    with open(trace_path, "w", encoding="utf-8") as f:
                        f.write(final_state.runtime_context.trace.model_dump_json(indent=2))
                    logger.info(f"Trace report saved to {trace_path}")
                except Exception as e:
                    logger.error(f"Failed to save trace report: {e}")

            # 5. Save Scan Manifest
            try:
                from schemas.manifests import ScanManifest
                import json
                
                plugins_used = []
                tool_failures = []
                if hasattr(final_state, 'logs') and final_state.logs:
                    for log in final_state.logs:
                        if hasattr(log, 'tool'):
                            plugins_used.append(log.tool)
                            if not log.success:
                                tool_failures.append(log.tool)
                                
                runtime_ms = 0.0
                if final_state.target and final_state.target.start_time:
                    end_time = datetime.datetime.now(datetime.timezone.utc)
                    runtime_ms = (end_time - final_state.target.start_time).total_seconds() * 1000
                    
                planner_decisions = []
                skipped_nodes = []
                if final_state.task_queue:
                    planner_decisions = [t.name for t in final_state.task_queue]
                    
                manifest = ScanManifest(
                    plugins_used=list(set(plugins_used)),
                    plugin_versions={}, # Simplified for now
                    runtime_ms=runtime_ms,
                    profile=config.profile.value if hasattr(config, "profile") else "default",
                    skipped_nodes=skipped_nodes,
                    planner_decisions=planner_decisions,
                    tool_failures=list(set(tool_failures)),
                    quality_score=0.0
                )
                
                manifest_path = __import__('os').path.join("workspaces", domain, "sessions", job_id, "manifest.json")
                with open(manifest_path, "w", encoding="utf-8") as f:
                    f.write(manifest.model_dump_json(indent=2))
                logger.info(f"Scan manifest saved to {manifest_path}")
            except Exception as e:
                logger.error(f"Failed to save scan manifest: {e}")
        else:
            if self._persistence_service:
                self._persistence_service.update_session(job_id, "failed")
                
        return job_id

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self._registry.get_job(job_id)
        status_dict = None
        if job:
            status_dict = {
                "job_id": job.job_id,
                "target": job.target_domain,
                "status": job.status.value,
                "progress": job.progress,
                "current_stage": job.current_stage,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "error": job.error,
                "workspace_path": f"workspace/sessions/{job_id}",
                "finding_count": 0,
                "report_count": 0
            }
            
        # Fallback to persistence service if not in registry
        if not status_dict and self._persistence_service:
            session = self._persistence_service.get_session(job_id)
            if session:
                status_dict = {
                    "job_id": session.session_id,
                    "target": session.target_domain,
                    "status": session.status,
                    "progress": 100.0 if session.status in ["completed", "failed", "cancelled"] else 0.0,
                    "current_stage": "unknown",
                    "started_at": session.started_at,
                    "completed_at": session.finished_at,
                    "error": None,
                    "workspace_path": f"workspace/sessions/{job_id}",
                    "finding_count": 0,
                    "report_count": 0
                }
                
        # Augment with counts from persistence if available
        if status_dict and self._persistence_service:
            try:
                # Use a new context to avoid messing up active transactions
                with self._persistence_service._get_session() as db:
                    reports = self._persistence_service.report_repo.get_by_session(db, job_id)
                    findings = self._persistence_service.finding_repo.get_by_session(db, job_id)
                    status_dict["report_count"] = len(reports)
                    status_dict["finding_count"] = len(findings)
            except Exception:
                pass
                
        return status_dict

    def cancel_scan(self, job_id: str) -> bool:
        cancelled = self._adapter.cancel(job_id)
        if cancelled and self._persistence_service:
            self._persistence_service.update_session(job_id, "cancelled")
        return cancelled

    def get_report(self, job_id: str, format: str = "json"):
        from schemas.generated_report import GeneratedReport
        
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
