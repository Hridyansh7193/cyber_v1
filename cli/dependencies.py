from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter
from services.scan_service import ScanService
from services.report_service import ReportService
from services.persistence_service import PersistenceService
from runtime.workspace import WorkspaceManager
from services.workspace_service import WorkspaceService
from config.loader import load_config
from pathlib import Path

def _create_default_config() -> BugHunterConfig:
    """Load the packaged defaults rather than a stale, duplicated config.

    The previous hard-coded values capped Dalfox at 60 seconds even though
    ``config/defaults/timeouts.yaml`` configures its 600-second scan timeout.
    Resolve the path from this module so the installed CLI works outside the
    repository root too.
    """
    config_dir = Path(__file__).resolve().parents[1] / "config"
    return load_config(config_dir)

registry = JobRegistry()
default_config = _create_default_config()

adapter = OrchestratorAdapter(registry, default_config)

persistence_service = PersistenceService()
workspace_manager = WorkspaceManager()
workspace_service = WorkspaceService(workspace_manager)
report_service = ReportService()
scan_service = ScanService(adapter, registry, persistence_service, report_service, workspace_service)
