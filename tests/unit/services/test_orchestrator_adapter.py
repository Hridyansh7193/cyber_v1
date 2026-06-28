import pytest
from unittest.mock import Mock, patch
from services.orchestrator_adapter import OrchestratorAdapter
from services.job_registry import JobRegistry, JobStatus
from config.schemas import BugHunterConfig
from schemas.target import TargetState
from schemas.generated_report import GeneratedReport
from schemas.report import ReportFormat
from datetime import datetime, timezone
import uuid

def test_adapter_successful_execution():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    mock_app = Mock()
    mock_app.stream.return_value = [{"stage1": {}}, {"stage2": {}}]
    
    with patch("services.orchestrator_adapter.build_graph", return_value=mock_app):
        adapter = OrchestratorAdapter(registry, config)
        job_id = registry.create_job("example.com")
        target = TargetState(domain="example.com", session_id=job_id, start_time=datetime.now(timezone.utc))
        adapter.run_scan(job_id, target)
        
        job = registry.get_job(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.progress == 100.0

def test_adapter_pipeline_failure():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    mock_app = Mock()
    mock_app.stream.side_effect = RuntimeError("Graph execution failed")
    
    with patch("services.orchestrator_adapter.build_graph", return_value=mock_app):
        adapter = OrchestratorAdapter(registry, config)
        job_id = registry.create_job("example.com")
        target = TargetState(domain="example.com", session_id=job_id, start_time=datetime.now(timezone.utc))
        adapter.run_scan(job_id, target)
        
        job = registry.get_job(job_id)
        assert job.status == JobStatus.FAILED
        assert "Graph execution failed" in job.error

def test_adapter_cancellation():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    adapter = OrchestratorAdapter(registry, config)
    
    # We want to yield one item, then have the status change to cancelled, then yield another item
    def mock_stream(*args, **kwargs):
        yield {"stage1": {}}
        registry.update_status(job_id, JobStatus.CANCELLED)
        yield {"stage2": {}}
        
    mock_app = Mock()
    mock_app.stream.side_effect = mock_stream
    
    with patch("services.orchestrator_adapter.build_graph", return_value=mock_app):
        adapter = OrchestratorAdapter(registry, config)
        job_id = registry.create_job("example.com")
        target = TargetState(domain="example.com", session_id=job_id, start_time=datetime.now(timezone.utc))
        adapter.run_scan(job_id, target)
        
        job = registry.get_job(job_id)
        assert job.status == JobStatus.CANCELLED
        # Progress shouldn't reach 100 since it cancelled mid-way
        assert job.progress < 100.0

