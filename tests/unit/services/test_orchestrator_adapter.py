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

def test_adapter_get_report():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    adapter = OrchestratorAdapter(registry, config)
    
    mock_db = Mock()
    gen_report = GeneratedReport(
        report_id=uuid.uuid4(),
        session_id="job-123",
        report_format=ReportFormat.JSON,
        format=ReportFormat.JSON,
        filename="report.json",
        mime_type="application/json",
        content='{"data": "test"}'
    )
    mock_db.get_reports_for_session.return_value = [gen_report]
    
    with patch("services.orchestrator_adapter.ReportRepository") as mock_repo_cls, \
         patch("services.orchestrator_adapter.get_db_session") as mock_session:
        
        mock_repo = mock_repo_cls.return_value
        mock_repo.get_by_session.return_value = [gen_report]
        
        mock_session.return_value.__enter__.return_value = Mock()
        
        report = adapter.get_report("job-123")
        assert report is not None
        assert len(report) == 1
        assert report[0].content == '{"data": "test"}'

def test_adapter_submit_scan():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    with patch("services.orchestrator_adapter.build_graph"), \
         patch("services.orchestrator_adapter.threading.Thread") as mock_thread:
        adapter = OrchestratorAdapter(registry, config)
        target = TargetState(domain="example.com", session_id="job-123", start_time=datetime.now(timezone.utc))
        adapter.submit_scan("job-123", target)
        
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()
        assert "job-123" in adapter._threads

def test_adapter_get_status():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    with patch("services.orchestrator_adapter.build_graph"):
        adapter = OrchestratorAdapter(registry, config)
        
        assert adapter.get_status("missing") is None
        
        job_id = registry.create_job("example.com")
        status = adapter.get_status(job_id)
        assert status is not None
        assert status["status"] == "pending"
        assert status["job_id"] == job_id
        
def test_adapter_cancel():
    registry = JobRegistry()
    config = BugHunterConfig(
        settings={"scan_depth": 1, "max_concurrency": 10, "log_level": "INFO"},
        llm={"provider": "dummy", "default_model": "dummy", "timeout": 30},
        tools={"tool_paths": {}, "docker_container_names": {}, "wordlists": {}, "enable_flags": {}},
        timeouts={"subfinder_timeout": 60, "nuclei_timeout": 60, "dalfox_timeout": 60, "ffuf_timeout": 60, "global_timeout": 3600},
        reporting={"report_formats": ["json"], "output_directories": {}}
    )
    with patch("services.orchestrator_adapter.build_graph"):
        adapter = OrchestratorAdapter(registry, config)
        
        assert adapter.cancel("missing") is False
        
        job_id = registry.create_job("example.com")
        assert adapter.cancel(job_id) is True
        
        status = adapter.get_status(job_id)
        assert status["status"] == "cancelled"
