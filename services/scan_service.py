from typing import Dict, Any, Optional
from services.orchestrator_adapter import OrchestratorAdapter
from services.job_registry import JobRegistry, JobStatus
from services.target_service import TargetService
from config.schemas import BugHunterConfig

class ScanService:
    """Orchestrates scan execution via the OrchestratorAdapter."""
    
    def __init__(self, adapter: OrchestratorAdapter, registry: JobRegistry):
        self._adapter = adapter
        self._registry = registry

    def submit_scan(self, domain: str, config: BugHunterConfig, metadata: dict = None) -> str:
        job_id = self._registry.create_job(domain, metadata)
        target = TargetService.normalize_target(domain, job_id, metadata)
        self._adapter.submit_scan(job_id, target)
        return job_id
        
    def run_scan_sync(self, domain: str, config: BugHunterConfig, metadata: dict = None) -> str:
        job_id = self._registry.create_job(domain, metadata)
        target = TargetService.normalize_target(domain, job_id, metadata)
        self._adapter.run_scan(job_id, target)
        return job_id

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._adapter.get_status(job_id)

    def cancel_scan(self, job_id: str) -> bool:
        return self._adapter.cancel(job_id)
