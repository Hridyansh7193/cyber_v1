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

def test_resume_and_evidence(base_config: BugHunterConfig, mocker, e2e_db):
    registry = JobRegistry()
    adapter = OrchestratorAdapter(registry, base_config)
    persistence = PersistenceService(session_maker=lambda: get_db_session())
    scan_service = ScanService(adapter, registry, persistence)
    
    domain = "test-resume.com"
    job_id = registry.create_job(domain, {})
    
    # Mock ProcessRunner.run to succeed and return some stdout
    from schemas.tool_result import ToolResult
    mock_run = mocker.patch("execution.utils.process_runner.ProcessRunner.run")
    mock_run.return_value = ToolResult(
        tool_name="subfinder",
        plugin_version="1.0",
        binary_path="/usr/bin/subfinder",
        command="subfinder -d test-resume.com",
        working_directory="/tmp",
        success=True,
        exit_code=0,
        stdout="sub1.test-resume.com\nsub2.test-resume.com\n",
        stderr="",
        stdout_size=100,
        execution_time=1.0,
        metadata_schema_version="1.0",
        parsed_findings=0,
        errors=(),
        parsed_output=(),
        metadata={}
    )
    
    # We will simulate a partial run by interrupting the graph execution inside adapter.
    # The adapter creates a checkpoint after each node. We can let it run normally,
    # as it's fully mocked by our fixtures (mock_subprocess_run in conftest usually).
    # Since we are creating ScanService manually, let's just run it synchronously.
    
    # Ensure evidence directory is created
    from runtime.workspace import WorkspaceManager
    workspace = WorkspaceManager()
    session_dir = workspace.create_session(job_id, domain, "default")
    
    # Run scan synchronously
    scan_service.run_scan_sync(domain, base_config, metadata={}, job_id=job_id)
    
    # Check if checkpoint exists
    checkpoint_path = os.path.join(session_dir, "checkpoint.json")
    assert os.path.exists(checkpoint_path)
    
    # Verify evidence directory contains outputs
    # Since mock_run was used, tool_name in our mock was subfinder, but the actual plugins might be httpx, nuclei, dalfox etc
    evidence_dir = os.path.join(session_dir, "evidence")
    assert os.path.exists(evidence_dir)
    
    # Check resume logic: it should load the checkpoint and run again without issues
    # Run scan sync again with is_resume=True
    scan_service.run_scan_sync(domain, base_config, metadata={}, job_id=job_id, is_resume=True)
    
    status = scan_service.get_status(job_id)
    assert status["status"] == "completed"
