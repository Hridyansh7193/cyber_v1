import yaml
import json
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter
from services.scan_service import ScanService
from services.report_service import ReportService
from services.persistence_service import PersistenceService
from runtime.workspace import WorkspaceManager
from services.workspace_service import WorkspaceService

def _create_default_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )

registry = JobRegistry()
default_config = _create_default_config()

adapter = OrchestratorAdapter(registry, default_config)

persistence_service = PersistenceService()
workspace_manager = WorkspaceManager()
workspace_service = WorkspaceService(workspace_manager)
report_service = ReportService()
scan_service = ScanService(adapter, registry, persistence_service, report_service, workspace_service)
