import pytest
from config.schemas import BugHunterConfig
from services.job_registry import JobRegistry
from services.orchestrator_adapter import OrchestratorAdapter
from services.scan_service import ScanService
from runtime.workspace import WorkspaceManager
from storage.database import init_db
from storage.models import Base

def setup_test_db():
    engine = init_db("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine

from services.persistence_service import PersistenceService
from services.report_service import ReportService
from services.workspace_service import WorkspaceService

@pytest.fixture
def mock_config():
    return BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {"recon": True, "js": True, "api": True, "vuln": True}},
        timeouts={"subfinder_timeout": 1, "nuclei_timeout": 1, "dalfox_timeout": 1, "ffuf_timeout": 1, "global_timeout": 5},
        reporting={"report_formats": ["json", "markdown"], "output_directories": {}}
    )

@pytest.fixture
def temp_workspace(tmp_path):
    ws = WorkspaceManager(root_dir=str(tmp_path / "workspace"))
    ws.initialize()
    return ws


def test_real_scan_pipeline(mock_config, temp_workspace, monkeypatch):
    # Initialize DB (in-memory for tests)
    setup_test_db()
    
    # Setup Services
    registry = JobRegistry()
    adapter = OrchestratorAdapter(registry, mock_config)
    persistence = PersistenceService()
    report_svc = ReportService()
    workspace_svc = WorkspaceService(temp_workspace)
    scan_service = ScanService(adapter, registry, persistence, report_svc, workspace_svc)
    
    from execution.utils.process_runner import ProcessRunner, ProcessResult
    from services.target_resolver import TargetResolver
    
    def mock_run(command, tool_name, cwd=None, timeout=None):
        return ProcessResult(exit_code=0, stdout="mock output", stderr="", execution_time=0.1)
    
    def mock_resolve(self, state):
        return state.model_copy(update={"hostname": state.domain, "resolved_url": f"http://{state.domain}", "scheme": "http", "alive": True})
        
    class MockDoctorReport:
        summary_fail = 0
        summary_pass = 10
        summary_warn = 0
        
    def mock_diagnose(self):
        return MockDoctorReport()

    from runtime.doctor import Doctor
    monkeypatch.setattr(Doctor, "diagnose", mock_diagnose)
    monkeypatch.setattr(ProcessRunner, "run", mock_run)
    monkeypatch.setattr(TargetResolver, "resolve_target", mock_resolve)
    
    # 1. Submit scan synchronously (for testing)
    domain = "example.local"
    # Execute scan synchronously using ScanService
    job_id = scan_service.run_scan_sync(domain, mock_config)
    
    status = registry.get_job(job_id)
    assert status.status.value == "completed", "Job failed or timed out"
    
    # Reports should be generated in the workspace
    reports_dir = workspace_svc.workspace_manager.get_session_dir(domain, job_id) / "reports"
    reports = list(reports_dir.glob("*.json")) + list(reports_dir.glob("*.md"))
    assert len(reports) > 0, "No reports found"
    
