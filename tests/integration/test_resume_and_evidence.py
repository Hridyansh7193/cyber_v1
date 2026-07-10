import pytest
import os
import json
import time
from pathlib import Path

from config.schemas import BugHunterConfig
from services.scan_service import ScanService
from services.orchestrator_adapter import OrchestratorAdapter
from services.job_registry import JobRegistry, JobStatus
from services.persistence_service import PersistenceService
from storage.database import get_db_session

@pytest.fixture
def test_config():
    return BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {"recon": True, "js": True, "api": True, "vuln": True}},
        timeouts={"subfinder_timeout": 1, "nuclei_timeout": 1, "dalfox_timeout": 1, "ffuf_timeout": 1, "global_timeout": 5},
        reporting={"report_formats": ["json", "markdown"], "output_directories": {}}
    )

@pytest.mark.skip(reason="Needs update for Milestone 3 TaskQueue orchestration logic")
def test_resume_and_evidence(test_config, monkeypatch, tmp_path):
    import storage.models as models
    from storage.database import get_engine, override_db
    
    db_path = tmp_path / "integration_bughunter.db"
    db_url = f"sqlite:///{db_path}"
    override_db(db_url)
    
    # Create tables
    engine = get_engine()
    models.Base.metadata.create_all(engine)

    registry = JobRegistry()
    adapter = OrchestratorAdapter(registry, test_config)
    persistence = PersistenceService()
    scan_service = ScanService(adapter, registry, persistence)
    
    domain = "test-resume.com"
    job_id = registry.create_job(domain, {})
    
    # Mock ProcessRunner.run to succeed and return some stdout
    from execution.utils.process_runner import ProcessResult
    
    def mock_run(command, tool_name, cwd=None, timeout=None):
        return ProcessResult(
            exit_code=0,
            stdout="sub1.test-resume.com\nsub2.test-resume.com\n",
            stderr="",
            execution_time=1.0,
            binary_path="/usr/bin/subfinder",
            command="subfinder -d test-resume.com",
            cwd="/tmp",
            error_message=""
        )
        
    import execution.utils.process_runner
    monkeypatch.setattr(execution.utils.process_runner.ProcessRunner, "run", mock_run)
    
    # We will simulate a partial run by interrupting the graph execution inside adapter.
    # The adapter creates a checkpoint after each node. We can let it run normally,
    # as it's fully mocked by our fixtures (mock_subprocess_run in conftest usually).
    # Since we are creating ScanService manually, let's just run it synchronously.
    
    # Ensure evidence directory is created
    from runtime.workspace import WorkspaceManager
    workspace = WorkspaceManager()
    session_dir = workspace.create_session(job_id, domain, "default")
    
    # Run scan synchronously
    scan_service.run_scan_sync(domain, test_config, metadata={}, job_id=job_id)
    
    # Check if checkpoint exists
    checkpoint_path = os.path.join(session_dir, "checkpoint.json")
    assert os.path.exists(checkpoint_path)
    
    # Verify evidence directory contains outputs
    # Since mock_run was used, tool_name in our mock was subfinder, but the actual plugins might be httpx, nuclei, dalfox etc
    evidence_dir = os.path.join(session_dir, "evidence")
    assert os.path.exists(evidence_dir)
    
    # Check resume logic: it should load the checkpoint and run again without issues
    # Run scan sync again with is_resume=True
    scan_service.run_scan_sync(domain, test_config, metadata={}, job_id=job_id, is_resume=True)
    
    status = scan_service.get_status(job_id)
    assert status["status"] == "completed"
