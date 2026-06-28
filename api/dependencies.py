from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter
from services.scan_service import ScanService
from services.report_service import ReportService
from fastapi import Request

# Global singleton instances for API
_registry = JobRegistry()

def _create_default_config() -> BugHunterConfig:
    return BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )

_default_config = _create_default_config()
_adapter = OrchestratorAdapter(_registry, _default_config)
from services.persistence_service import PersistenceService
from runtime.workspace import WorkspaceManager
from services.workspace_service import WorkspaceService

from services.analytics_service import AnalyticsService

_persistence_service = PersistenceService()
_workspace_manager = WorkspaceManager()
_workspace_service = WorkspaceService(_workspace_manager)
_report_service = ReportService()
_scan_service = ScanService(_adapter, _registry, _persistence_service, _report_service, _workspace_service)
_analytics_service = AnalyticsService()

def get_scan_service() -> ScanService:
    return _scan_service

def get_report_service() -> ReportService:
    return _report_service

def get_analytics_service() -> AnalyticsService:
    return _analytics_service

def get_default_config() -> BugHunterConfig:
    return _default_config
